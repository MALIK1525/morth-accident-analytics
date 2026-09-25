"""
Supporting-dataset ingestion engine for the MoRTH analytics platform.

Drop-in folder: data/supporting_csv/*.csv
- Every CSV placed here is inspected, validated and registered.
- Recognised MoRTH schemas (collision, violation, licence, safety-device,
  road-user fatalities, victim x crime-vehicle matrix, cities, exposure,
  state x year, annual totals) are normalised into tidy tables.
- Unrecognised files are registered as UNRECOGNIZED (listed, never visualised).
- Nothing is fabricated: absent files simply stay unavailable.

Documented source schemas come from the project's DATASET_REGISTER /
ANALYSIS_READY_DATASETS audit (MoRTH Annual Report 2024 derived CSVs).
"""
import os
import re
import glob
import pandas as pd
import numpy as np

SUPPORTING_DIR = os.path.join("data", "supporting_csv")


def parse_indian_int(value):
    """Parse counts in Indian comma format ('4,87,707'), '(P)' provisional
    flags, 'NA'/'' missing markers. Returns int or None (never 0 for missing)."""
    if value is None:
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, float):
        return int(value) if pd.notnull(value) else None
    s = str(value).strip().replace('\ufeff', '')
    if s == '' or s.upper() in ('NA', 'N/A', '-', '--', 'NIL'):
        return None
    s = re.sub(r'\(P\)', '', s, flags=re.IGNORECASE).strip()
    s = s.replace(',', '')
    try:
        return int(float(s))
    except ValueError:
        return None


def parse_pct(value):
    if value is None:
        return None
    s = str(value).strip().replace('%', '').replace(',', '')
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def _is_share_row(first_cell):
    s = str(first_cell).strip().lower().replace('\ufeff', '')
    return 'share' in s or s in ('%', '% change')


def _norm_cols(df):
    df = df.copy()
    df.columns = [str(c).strip().replace('\ufeff', '') for c in df.columns]
    return df


def _find_col(df, *keywords):
    """First column whose lowercased name contains all keywords."""
    for c in df.columns:
        low = c.lower()
        if all(k in low for k in keywords):
            return c
    return None


class SupportingDataStore:
    """Loads, validates and registers every CSV in data/supporting_csv/."""

    # schema_key -> (catalog_ids it unlocks, granularity)
    SCHEMA_CATALOG = {
        'annual_totals': (['G1', 'G2', 'G3'], 'India-Year'),
        'collision': (['CL-01'], 'India-Year-Category'),
        'violation': (['CS-01'], 'India-Year-Cause'),
        'licence': (['DL-01'], 'India-Year-Category'),
        'safety_device': (['SD-01'], 'India-Year-Category'),
        'road_user': (['VH-01'], 'India-Year-Vehicle'),
        'victim_crime_matrix': (['VH-02'], 'India-Victim-CrimeVehicle'),
        'cities_overview': (['CT-01'], 'City-Year'),
        'cities_mode': (['CT-02'], 'City-Mode'),
        'cities_violation': (['CT-03'], 'City-Violation'),
        'licence': (['DL-01'], 'India-Year-Category'),
        'safety_device': (['SD-01'], 'India-Year-Category'),
        'exposure': (['EX-01'], 'India-Year-Exposure'),
        'states_accidents': (['G7', 'G8'], 'State-Year'),
        'states_fatalities': (['G7', 'G8'], 'State-Year'),
    }

    def __init__(self, directory=SUPPORTING_DIR):
        self.directory = directory
        self.registry = {}   # schema_key -> {filename, rows, years, granularity, status, warnings, table}
        self.unrecognized = []
        self.refresh()

    # ---------- public API ----------
    def refresh(self):
        self.registry = {}
        self.unrecognized = []
        if not os.path.isdir(self.directory):
            return
        for path in sorted(glob.glob(os.path.join(self.directory, '*.csv'))):
            self._ingest(path)

    def get(self, schema_key):
        return self.registry.get(schema_key)

    def available_schemas(self):
        return sorted(self.registry.keys())

    def summary(self):
        return {
            'supporting_dir': self.directory,
            'files_found': len(self.registry) + len(self.unrecognized),
            'schemas_available': self.available_schemas(),
            'unrecognized_files': self.unrecognized,
            'registry': {
                k: {kk: v[kk] for kk in ('filename', 'rows', 'years', 'granularity', 'status', 'warnings')}
                for k, v in self.registry.items()
            },
        }

    def refresh_catalog_statuses(self, catalog):
        """Flip catalog entries to AVAILABLE when their schema is loaded."""
        schema_to_ids = {}
        for schema, (ids, _) in self.SCHEMA_CATALOG.items():
            for i in ids:
                schema_to_ids.setdefault(i, schema)
        for entry in catalog:
            schema = schema_to_ids.get(entry['id'])
            if schema and schema in self.registry:
                reg = self.registry[schema]
                entry['status'] = 'AVAILABLE'
                entry['source'] = f"MoRTH AR 2024 CSV: {reg['filename']}"
                entry['coverage'] = reg['years']
                entry['granularity'] = reg['granularity']
        return catalog

    # ---------- internals ----------
    def _ingest(self, path):
        fname = os.path.basename(path)
        try:
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
        except Exception as e:
            self.unrecognized.append({'filename': fname, 'reason': f'unreadable: {e}'})
            return
        df = _norm_cols(df)
        for schema, parser in [
            ('collision', self._parse_category_years),
            ('violation', self._parse_category_years),
            ('road_user', self._parse_category_years),
            ('licence', self._parse_category_years),
            ('safety_device', self._parse_safety_device),
            ('victim_crime_matrix', self._parse_matrix),
            ('cities_overview', self._parse_cities),
            ('cities_mode', self._parse_cities),
            ('cities_violation', self._parse_cities),
            ('exposure', self._parse_exposure),
            ('states_accidents', self._parse_states),
            ('states_fatalities', self._parse_states),
            ('annual_totals', self._parse_annual),
        ]:
            if schema in self.registry:
                continue
            try:
                table = parser(df, fname)
            except Exception:
                table = None
            if table is not None and not table.empty:
                years = sorted(table['Year'].dropna().unique().tolist()) if 'Year' in table.columns else []
                self.registry[schema] = {
                    'filename': fname,
                    'rows': int(len(table)),
                    'years': f"{min(years)}-{max(years)}" if years else 'n/a',
                    'granularity': self.SCHEMA_CATALOG[schema][1],
                    'status': 'AVAILABLE',
                    'warnings': self._validate(table, schema),
                    'table': table,
                }
                return
        self.unrecognized.append({'filename': fname, 'reason': 'no recognised MoRTH schema matched'})

    def _data_rows(self, df):
        """Drop '% share' annotation rows; return (data_df, first_col)."""
        first = df.columns[0]
        mask = ~df[first].apply(_is_share_row)
        return df[mask].copy(), first

    def _year_cols(self, df, years=(2023, 2024)):
        """Map {year: {accidents_col, killed_col, injured_col}} from headers."""
        out = {}
        for y in years:
            acc = _find_col(df, str(y), 'accident') or _find_col(df, str(y), 'total')
            kil = _find_col(df, str(y), 'kill')
            inj = _find_col(df, str(y), 'injur')
            if acc or kil or inj:
                out[y] = (acc, kil, inj)
        return out

    def _parse_category_years(self, df, fname):
        """Generic Category x Year (accidents/killed/injured) parser for
        collision / violation / road-user / licence tables."""
        data, first = self._data_rows(df)
        # drop Total rows (kept separately for validation)
        totals = data[data[first].str.strip().str.lower() == 'total']
        data = data[data[first].str.strip().str.lower() != 'total']
        ymap = self._year_cols(df)
        if not ymap or data.empty:
            return None
        # sanity: first column must look categorical (non-numeric labels)
        if data[first].apply(lambda x: str(x).strip().replace('.', '').isdigit()).all():
            return None
        rows = []
        for _, r in data.iterrows():
            cat = str(r[first]).strip()
            if not cat:
                continue
            for y, (acc, kil, inj) in ymap.items():
                rows.append({
                    'Category': cat,
                    'Year': y,
                    'Accidents': parse_indian_int(r[acc]) if acc else None,
                    'Killed': parse_indian_int(r[kil]) if kil else None,
                    'Injured': parse_indian_int(r[inj]) if inj else None,
                })
        table = pd.DataFrame(rows)
        if table.empty or table[['Accidents', 'Killed', 'Injured']].isna().all().all():
            return None
        return table

    def _parse_safety_device(self, df, fname):
        low = ' '.join(df.columns).lower()
        if 'helmet' not in low and 'seatbelt' not in low and 'seat belt' not in low:
            return None
        data, first = self._data_rows(df)
        rows = []
        for _, r in data.iterrows():
            cat = str(r[first]).strip()
            if not cat or cat.lower() == 'total':
                continue
            row = {'Category': cat, 'Year': 2024}
            for c in df.columns[1:]:
                row[c] = parse_indian_int(r[c])
            rows.append(row)
        table = pd.DataFrame(rows)
        return table if not table.empty else None

    def _parse_matrix(self, df, fname):
        low = ' '.join(df.columns).lower()
        if 'victim' not in low and 'crime' not in low:
            # victim x crime-vehicle matrix may just be a wide 9x9 table
            if len(df.columns) < 6 or len(df) < 5:
                return None
        data, first = self._data_rows(df)
        if data.empty or len(df.columns) < 4:
            return None
        # tidy: melt wide matrix
        melted = data.melt(id_vars=[first], var_name='Crime_Vehicle', value_name='Killed')
        melted = melted.rename(columns={first: 'Victim'})
        melted['Killed'] = melted['Killed'].apply(parse_indian_int)
        melted['Year'] = 2024
        melted = melted[melted['Killed'].notna()]
        return melted if not melted.empty else None

    def _parse_cities(self, df, fname):
        low = ' '.join(df.columns).lower()
        if 'city' not in low:
            return None
        data, first = self._data_rows(df)
        data = data[~data[first].str.strip().str.lower().isin(('total', 'sl no', 's.no'))]
        if data.empty:
            return None
        rows = []
        for _, r in data.iterrows():
            city = str(r[first]).strip()
            if not city or city.replace('.', '').isdigit():
                continue
            base = {'City': city}
            for c in df.columns[1:]:
                cl = c.lower()
                y = 2024 if '2024' in c else (2023 if '2023' in c else None)
                val = parse_indian_int(r[c])
                base[c] = val
                _ = y
            rows.append(base)
        table = pd.DataFrame(rows)
        return table if not table.empty else None

    def _parse_exposure(self, df, fname):
        low = ' '.join(df.columns).lower()
        if 'vehicle' not in low or 'year' not in low:
            return None
        ycol = _find_col(df, 'year')
        if not ycol:
            return None
        rows = []
        for _, r in df.iterrows():
            try:
                y = int(str(r[ycol]).strip()[:4])
            except ValueError:
                continue
            row = {'Year': y}
            for c in df.columns:
                if c == ycol:
                    continue
                cl = c.lower()
                if 'rate' in cl or 'density' in cl or 'per ' in cl:
                    row[c] = parse_pct(r[c])
                else:
                    row[c] = parse_indian_int(r[c])
            rows.append(row)
        table = pd.DataFrame(rows)
        return table if not table.empty else None

    def _parse_states(self, df, fname):
        low = ' '.join(df.columns).lower()
        if 'state' not in low:
            return None
        data, first = self._data_rows(df)
        data = data[~data[first].str.strip().str.lower().isin(('total',))]
        # need several year columns to qualify as state x year
        year_cols = [c for c in df.columns if re.search(r'20\d{2}', c)]
        if len(year_cols) < 2 or data.empty:
            return None
        rows = []
        for _, r in data.iterrows():
            st = str(r[first]).strip()
            if not st or st.replace('.', '').isdigit():
                continue
            for c in year_cols:
                m = re.search(r'(20\d{2})', c)
                if not m:
                    continue
                rows.append({'State': st, 'Year': int(m.group(1)),
                             'Variable': c, 'Value': parse_indian_int(r[c])})
        table = pd.DataFrame(rows)
        return table if not table.empty else None

    def _parse_annual(self, df, fname):
        ycol = _find_col(df, 'year')
        if not ycol:
            return None
        acc = _find_col(df, 'accident')
        kil = _find_col(df, 'fatal', ) or _find_col(df, 'kill') or _find_col(df, 'death')
        if not acc and not kil:
            return None
        rows = []
        for _, r in df.iterrows():
            try:
                y = int(str(r[ycol]).strip()[:4])
            except ValueError:
                continue
            rows.append({'Year': y,
                         'Accidents': parse_indian_int(r[acc]) if acc else None,
                         'Killed': parse_indian_int(r[kil]) if kil else None})
        table = pd.DataFrame(rows)
        return table if not table.empty else None

    def _validate(self, table, schema):
        warnings = []
        if schema in ('collision', 'violation', 'road_user') and 'Killed' in table.columns:
            tot2024 = table[(table['Year'] == 2024)]['Killed'].sum(skipna=True)
            if tot2024 and abs(int(tot2024) - 177175) > 5000:
                warnings.append(f'2024 killed sum {int(tot2024):,} differs from MoRTH 177,175 — check share-row filtering.')
        return warnings

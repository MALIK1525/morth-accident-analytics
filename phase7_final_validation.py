"""Phase 7 final validation: area-weighting, boundary-cell sensitivity, Andaman check."""
import netCDF4 as nc, numpy as np, pandas as pd, geopandas as gpd, glob, json
from shapely.geometry import box

RAW="phase6_raw/weather/IMD"
shp=glob.glob("phase7_raw/boundaries/SOI/**/State Boundary.shp",recursive=True)[0]
g=gpd.read_file(shp)
NCOL=[c for c in g.columns if 'STAT' in c.upper() or 'NAME' in c.upper()][0]
g2=g[[NCOL,"geometry"]].to_crs("EPSG:4326")
g2=g2[~g2[NCOL].str.startswith("DISPUTED")].copy()
print("polys:",len(g2),flush=True)

d=nc.Dataset(f"{RAW}/RF25_2018.nc"); lon=np.array(d.variables["LONGITUDE"][:]); lat=np.array(d.variables["LATITUDE"][:]); d.close()
dlat=abs(lat[1]-lat[0]); dlon=abs(lon[1]-lon[0])
# cell area weight ~ cos(lat) (regular lon/lat grid)
cell_w=np.cos(np.deg2rad(lat)); cell_w/=cell_w.mean()
Lon,Lat=np.meshgrid(lon,lat); flat_lon=Lon.ravel(); flat_lat=Lat.ravel()
from shapely.geometry import Point
pts=gpd.GeoDataFrame({"lon":flat_lon,"lat":flat_lat},geometry=[Point(x,y) for x,y in zip(flat_lon,flat_lat)],crs="EPSG:4326")
jn=gpd.sjoin(pts,g2,how="left",predicate="within")
jn["state"]=jn[NCOL]
states=sorted(s for s in g2[NCOL].unique())
sidx={s:np.where(jn["state"].values==s)[0] for s in states}

# boundary-cell analysis: cell boxes vs polygons (vectorized per state)
tot_cells=len(flat_lon); assigned=int(jn["state"].notna().sum())
full_in=0; partial=0
state_boxfrac={}  # state -> dict cellidx->frac
for s in states:
    poly=g2[g2[NCOL]==s].geometry.union_all()
    idx=sidx[s]
    if len(idx)==0:
        state_boxfrac[s]={}; continue
    fr={}
    for ci in idx:
        b=box(flat_lon[ci]-dlon/2,flat_lat[ci]-dlat/2,flat_lon[ci]+dlon/2,flat_lat[ci]+dlat/2)
        inter=b.intersection(poly).area
        f=inter/b.area
        fr[ci]=f
        if f>0.999: full_in+=1
        else: partial+=1
    state_boxfrac[s]=fr
print(f"total={tot_cells} assigned={assigned} full={full_in} partial={partial}",flush=True)

# annual comparison equal vs area-weighted vs overlap-weighted
rows=[]; sens=[]
for y in range(2018,2025):
    dd=nc.Dataset(f"{RAW}/RF25_{y}.nc")
    rfm=np.ma.filled(dd.variables["RAINFALL"][:].astype(np.float64),np.nan); dd.close()
    T=flat=rfm.reshape(rfm.shape[0],-1)
    for s in states:
        idx=np.array(list(state_boxfrac[s].keys()))
        if len(idx)==0: continue
        fr=np.array([state_boxfrac[s][i] for i in idx])
        aw=cell_w[np.unravel_index(idx,(len(lat),len(lon)))[0]]
        vals=flat[:,idx]
        with np.errstate(all="ignore"):
            eq=np.nanmean(vals,axis=1)
            am=np.nansum(vals*aw,axis=1)/np.nansum(np.where(np.isnan(vals),np.nan,aw),axis=1)
            om=np.nansum(vals*fr,axis=1)/np.nansum(np.where(np.isnan(vals),np.nan,fr),axis=1)
        EQ=float(np.nansum(eq)); AM=float(np.nansum(am)); OM=float(np.nansum(om))
        cov=float(np.mean(~np.isnan(eq)))
        rows.append({"State":s,"Year":y,"Equal_Cell_Rainfall":round(EQ,1),"Area_Weighted_Rainfall":round(AM,1),
            "Absolute_Difference":round(abs(EQ-AM),2),"Relative_Difference_pct":round(100*abs(EQ-AM)/AM,3) if AM else None,
            "Valid_Days":int(np.sum(~np.isnan(eq)))})
        sens.append({"State_UT":s,"Year":y,"Centroid_Rainfall":round(EQ,1),"Overlap_Weighted_Rainfall":round(OM,1),
            "Absolute_Difference":round(abs(EQ-OM),2),"Relative_Difference_pct":round(100*abs(EQ-OM)/OM,3) if OM else None,
            "Boundary_Cells":int(np.sum(np.array(list(state_boxfrac[s].values()))<0.999)),
            "Status":"INSUFFICIENT_COVERAGE" if cov<0.9 else "OK"})
    print("year done",y,flush=True)
cmp_df=pd.DataFrame(rows); cmp_df.to_csv("area_weighting_comparison.csv",index=False)
pd.DataFrame(sens).to_csv("boundary_cell_sensitivity.csv",index=False)
r=cmp_df.dropna(subset=["Relative_Difference_pct"])
print("area-weight: max rel%",r.Relative_Difference_pct.max(),"mean",r.Relative_Difference_pct.mean())
s2=pd.DataFrame(sens).dropna(subset=["Relative_Difference_pct"])
print("overlap: max rel%",s2.Relative_Difference_pct.max(),"mean",s2.Relative_Difference_pct.mean())

# Andaman check
anam=g2[g2[NCOL]=="ANDAMAN & NICOBAR"]
poly=anam.geometry.union_all()
dd=nc.Dataset(f"{RAW}/RF25_2018.nc"); rfm=np.ma.filled(dd.variables["RAINFALL"][:].astype(np.float64),np.nan)
mask1day=np.isnan(rfm[0]).reshape(-1); dd.close()
boxes=[box(flat_lon[i]-dlon/2,flat_lat[i]-dlat/2,flat_lon[i]+dlon/2,flat_lat[i]+dlat/2) for i in range(len(flat_lon))]
inter=[b.intersects(poly) for b in boxes]
idx=np.where(inter)[0]
recs=[]
for i in idx:
    recs.append({"lon":flat_lon[i],"lat":flat_lat[i],"centroid_inside":bool(i in sidx.get("ANDAMAN & NICOBAR",[])),
        "day0_masked":bool(mask1day[i]),"frac_overlap":round(boxes[i].intersection(poly).area/boxes[i].area,3)})
ad=pd.DataFrame(recs); ad.to_csv("andaman_spatial_validation.csv",index=False)
print("andaman intersecting cells:",len(ad),"valid day0:",int((~mask1day[idx]).sum()))
# nearest valid cell distance
valid=np.where(~mask1day)[0]
from math import radians,sin,cos,asin,sqrt
def hav(a,b,c,d):
    a,b,c,d=map(radians,[a,b,c,d]); h=sin((c-a)/2)**2+cos(a)*cos(c)*sin((d-b)/2)**2; return 6371*2*asin(sqrt(h))
ctr=(np.mean([r["lon"] for r in recs]),np.mean([r["lat"] for r in recs])) if recs else (None,None)
dmin=min(hav(ctr[1],ctr[0],flat_lat[v],flat_lon[v]) for v in valid) if recs else None
print("nearest valid cell km from island centroid:",round(dmin,1) if dmin else None)
json.dump({"total_cells":tot_cells,"assigned":assigned,"full_inside":full_in,"partial":partial,
 "area_max_rel_pct":float(r.Relative_Difference_pct.max()),"area_mean_rel_pct":float(r.Relative_Difference_pct.mean()),
 "overlap_max_rel_pct":float(s2.Relative_Difference_pct.max()),"overlap_mean_rel_pct":float(s2.Relative_Difference_pct.mean()),
 "andaman_intersecting":len(ad),"andaman_valid_day0":int((~mask1day[idx]).sum()) if len(idx) else 0,
 "andaman_nearest_valid_km":round(dmin,1) if dmin else None},open("phase7_final_numbers.json","w"),indent=1)
print("saved",flush=True)

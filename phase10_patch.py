s = open('phase10b_tables.py').read()
old = 'pd.DataFrame([{"#":["see report Ch.6"]'
assert old in s, "pattern missing"
i = s.index(old)
j = s.index('}])', i) + 3
new = 'pd.DataFrame({"n":[1,2,3,4,5],"limitation":["no verified vehicle denominator","no Census 2021","humidity/visibility/fog/wind N/A","monthly accidents N/A","driver/vehicle/cause detail N/A"]})'
s = s[:i] + new + s[j:]
open('phase10b_tables.py', 'w').write(s)
print('patched ok')

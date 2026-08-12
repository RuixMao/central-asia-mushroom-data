import re

SPECIES=[
 ("agaricus_bisporus","双孢菇",["шампиньон","champignon","button mushroom"]),("pleurotus_ostreatus","平菇",["вешенк","oyster"]),("flammulina_velutipes","金针菇",["эноки","enoki"]),("lentinula_edodes","香菇",["шиитаке","shiitake"]),("pleurotus_eryngii","杏鲍菇",["эринги","королевская вешенка","king oyster"]),("auricularia","木耳",["муэр","wood ear"]),("morel","羊肚菌",["сморчок","morel"]),("maitake","舞茸",["маитаке","maitake"]),("porcini","牛肝菌",["белый гриб","боровик","porcini"]),("chanterelle","鸡油菌",["лисичка","chanterelle"]),("honey_fungus","蜜环菌",["опёнок","опенок","honey mushroom"]),("suillus","乳牛肝菌",["маслёнок","масленок"]),
]
EXCLUDED=["соус","mushroom sauce","суп","лапша","snack","экстракт","extract","мицелий","菌种"]
FORM_RULES=[("frozen",["заморож","frozen"]),("dried",["сушен","dried"]),("pickled",["марин","pickled"]),("canned",["консерв","canned"]),("powder",["порош","powder"]),("prepared_food",["соус","суп","лапша","готовое блюдо"]),("fresh",["свеж","fresh"])]

def classify(title,description="",category=""):
 text=" ".join([title,description,category]).lower()
 if any(term in text for term in EXCLUDED): return {"species_id":None,"product_form":"prepared_food" if any(x in text for x in ("соус","суп","лапша","готовое")) else "unknown","status":"excluded","confidence":1.0,"evidence":{"excluded_term":True}}
 hits=[(sid,name,term) for sid,name,terms in SPECIES for term in terms if term in text]
 form=next((value for value,terms in FORM_RULES if any(t in text for t in terms)),"fresh")
 if len({h[0] for h in hits})>1:return {"species_id":"mixed_species","product_form":"mixed","status":"mixed_species","confidence":.99,"evidence":{"terms":[h[2] for h in hits]}}
 if hits:return {"species_id":hits[0][0],"product_form":form,"status":"classified","confidence":.96,"evidence":{"term":hits[0][2],"field":"title_or_description"}}
 return {"species_id":"unknown_species","product_form":form,"status":"unknown","confidence":0.0,"evidence":{"reason":"no deterministic synonym match"}}

def parse_package(text):
 normalized=text.lower().replace(",",".")
 match=re.search(r"(\d+(?:\.\d+)?)\s*(kg|кг|g|гр|г)\b",normalized)
 if not match:return {"value":None,"unit":None,"quantity_kg":None}
 value=float(match.group(1));unit=match.group(2);kg=value if unit in ("kg","кг") else value/1000
 multiplier=re.search(r"[x×]\s*(\d+)",normalized)
 if multiplier:kg*=int(multiplier.group(1))
 return {"value":value,"unit":unit,"quantity_kg":kg}

def normalize_price(price,package_text):
 package=parse_package(package_text)
 return {**package,"price_per_kg":round(price/package["quantity_kg"],2) if price is not None and package["quantity_kg"] else None}

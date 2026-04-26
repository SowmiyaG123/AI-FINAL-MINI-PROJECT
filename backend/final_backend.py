import re,json,uuid,asyncio,logging,hashlib,io,random
from typing import Optional
from fastapi import FastAPI,UploadFile,File,Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx,uvicorn

logging.basicConfig(level=logging.INFO,format="%(asctime)s|%(levelname)s|%(message)s")
log=logging.getLogger("recipe-v6")
GROQ_KEY="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"
GROQ_URL="https://api.groq.com/openai/v1/chat/completions"
GROQ_MDL="llama3-70b-8192";CHROMA_DIR="./chroma_db";EMBED_MDL="all-MiniLM-L6-v2";CUTOFF=0.04
app=FastAPI(title="Recipe Assistant v6")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

IM={"chicken":["chicken","boneless chicken","chicken breast","chicken thigh","chicken pieces","grilled chicken"],"beef":["beef","ground beef","minced beef","steak","beef mince"],"pork":["pork","pork belly","bacon","pancetta","ham"],"lamb":["lamb","ground lamb","lamb chop","mutton","goat meat"],"salmon":["salmon","salmon fillet","smoked salmon"],"tuna":["tuna","canned tuna","tuna steak"],"cod":["cod","cod fillet","white fish"],"fish":["fish","fish fillet","sea bass","halibut","tilapia","basa","snapper"],"shrimp":["shrimp","prawn","prawns","tiger prawn","king prawn","jumbo shrimp"],"crab":["crab","crab meat"],"squid":["squid","calamari"],"eggs":["eggs","egg","egg yolk","egg white","boiled egg"],"milk":["milk","whole milk","skim milk","dairy milk"],"butter":["butter","unsalted butter","salted butter"],"cream":["cream","heavy cream","whipping cream","fresh cream","single cream"],"yogurt":["yogurt","curd","greek yogurt","plain yogurt","dahi","sour cream"],"cheese":["cheese","cheddar","mozzarella","feta","gouda"],"parmesan":["parmesan","parmigiano","grana padano","pecorino"],"paneer":["paneer","cottage cheese"],"ghee":["ghee","clarified butter","desi ghee"],"rice":["rice","basmati rice","cooked rice","jasmine rice","arborio rice","white rice","brown rice"],"pasta":["pasta","spaghetti","penne","fettuccine","linguine","fusilli","noodles","macaroni"],"bread":["bread","sandwich bread","sourdough","baguette","toast"],"flour":["flour","all purpose flour","plain flour","wheat flour","maida"],"oats":["oats","rolled oats","oatmeal","porridge oats"],"pizza dough":["pizza dough","pizza base"],"tomato":["tomato","tomatoes","cherry tomatoes","canned tomatoes","tomato puree","tomato paste"],"onion":["onion","onions","red onion","white onion","spring onion","shallot","scallion"],"garlic":["garlic","garlic cloves","minced garlic","garlic paste","garlic powder"],"ginger":["ginger","fresh ginger","ginger paste","ground ginger"],"spinach":["spinach","baby spinach","fresh spinach","palak"],"carrot":["carrot","carrots","baby carrots","grated carrot"],"potato":["potato","potatoes","sweet potato","aloo","yam"],"mushroom":["mushrooms","mushroom","portobello","button mushrooms","cremini","shiitake"],"bell pepper":["bell pepper","capsicum","red pepper","green pepper","yellow pepper"],"zucchini":["zucchini","courgette"],"avocado":["avocado","ripe avocado"],"cucumber":["cucumber"],"corn":["corn","sweet corn","corn kernels"],"peas":["peas","green peas","frozen peas"],"celery":["celery","celery stalks"],"broccoli":["broccoli","broccoli florets"],"cauliflower":["cauliflower","cauliflower florets","gobi","phool gobi"],"eggplant":["eggplant","aubergine","brinjal","baingan"],"cabbage":["cabbage","red cabbage","shredded cabbage"],"apple":["apple","apples","green apple","red apple","apple slices"],"mango":["mango","mangoes","mango pulp","ripe mango"],"banana":["banana","bananas","ripe banana","plantain"],"strawberry":["strawberry","strawberries","fresh strawberries","frozen strawberries"],"lemon":["lemon","lemon juice","lemon zest","citrus"],"lime":["lime","lime juice"],"orange":["orange","orange juice"],"blueberry":["blueberry","blueberries"],"raspberry":["raspberry","raspberries"],"peach":["peach","peaches"],"oil":["oil","vegetable oil","cooking oil","sunflower oil","canola oil"],"olive oil":["olive oil","extra virgin olive oil"],"coconut milk":["coconut milk","coconut cream"],"soy sauce":["soy sauce","soya sauce","light soy sauce","tamari"],"sugar":["sugar","granulated sugar","brown sugar","caster sugar","powdered sugar"],"honey":["honey","maple syrup"],"salt":["salt","sea salt","kosher salt"],"black pepper":["black pepper","pepper","ground pepper"],"cumin":["cumin","cumin seeds","jeera","ground cumin"],"cinnamon":["cinnamon","ground cinnamon","cinnamon stick"],"turmeric":["turmeric","haldi","turmeric powder"],"garam masala":["garam masala","garam masala powder"],"chili":["chili","chilli","red chili","green chili","chili powder","chilli flakes","cayenne","kashmiri chili"],"paprika":["paprika","smoked paprika"],"coriander powder":["coriander powder","dhania powder","ground coriander"],"cardamom":["cardamom","green cardamom","elaichi"],"saffron":["saffron","kesar"],"oregano":["oregano","dried oregano"],"thyme":["thyme","fresh thyme"],"rosemary":["rosemary"],"dill":["dill","fresh dill"],"mint":["mint","fresh mint","pudina"],"basil":["basil","fresh basil","thai basil"],"cilantro":["cilantro","coriander","fresh coriander","dhania"],"baking powder":["baking powder","raising agent"],"baking soda":["baking soda","bicarbonate of soda"],"vanilla extract":["vanilla extract","vanilla essence","vanilla"],"cocoa powder":["cocoa powder","cacao powder"],"chocolate":["chocolate","dark chocolate","milk chocolate","chocolate chips"],"cream cheese":["cream cheese","philadelphia","mascarpone"],"tomato sauce":["tomato sauce","marinara","passata","pizza sauce"],"caramel sauce":["caramel sauce","caramel"],"whipped cream":["whipped cream"],"green curry paste":["green curry paste","thai green curry paste"],"fish sauce":["fish sauce","nam pla"],"nuts":["nuts","walnuts","almonds","cashews","peanuts","pine nuts","pistachios"],"sesame oil":["sesame oil","toasted sesame oil"],"chickpeas":["chickpeas","chana","garbanzo beans","canned chickpeas"],"lentils":["lentils","red lentil","green lentil","black lentil","masoor dal","moong dal","dal"],"kidney beans":["kidney beans","rajma","canned kidney beans"],"tofu":["tofu","firm tofu","silken tofu"],"vanilla ice cream":["vanilla ice cream","ice cream","gelato"],"wafers":["wafers","graham crackers","digestive biscuits"],"white wine":["white wine","dry white wine","cooking wine"],"vegetable stock":["vegetable stock","vegetable broth","veg stock"],"chicken broth":["chicken broth","chicken stock"],"biryani masala":["biryani masala","biryani spice mix"],"chana masala":["chana masala","chole masala"],"spring onion":["spring onion","scallion","green onion"],"taco shells":["taco shells","tortillas","corn tortillas"],"bay leaf":["bay leaf","bay leaves","tej patta"]}
SEAFOOD={"fish","salmon","tuna","cod","shrimp","crab","squid","seafood","halibut","tilapia","sea bass"}
CAN:dict[str,str]={}
for c,vs in IM.items():
    CAN[c]=c
    for v in vs: CAN[v.lower().strip()]=c
def norm(s): return re.sub(r"\s+"," ",s.lower().strip())
def canon(r):
    r=norm(r)
    if r in CAN: return CAN[r]
    for a in sorted(CAN,key=len,reverse=True):
        if len(a)>2 and a in r: return CAN[a]
    return r
def detect_diet(t):
    t=norm(t)
    if re.search(r'\bnon[- ]?veg(etarian)?\b|\bmeat\b',t): return ["non-veg"],[]
    de,dm=[],[]
    if re.search(r'\bvegan\b',t): de.append("vegan");dm=["chicken","beef","pork","lamb","fish","salmon","shrimp","eggs","milk","cream","butter","cheese","parmesan","ghee","yogurt","paneer","tuna","cod","crab","squid"]
    elif re.search(r'\bveg(etarian)?\b|\bno meat\b|\bplant.based\b',t): de.append("vegetarian");dm=["chicken","beef","pork","lamb","fish","salmon","shrimp","tuna","cod","crab","squid"]
    if re.search(r'\bpescatarian\b',t): de.append("pescatarian");dm=["chicken","beef","pork","lamb"]
    return de,dm
MEAL_KW={"dessert":["dessert","sweet","sweets","cake","pudding","treat","ice cream","cheesecake","crumble","halwa"],"breakfast":["breakfast","morning","brunch"],"soup":["soup"],"drink":["drink","smoothie","lassi","juice","shake"],"salad":["salad"],"snack":["snack"],"lunch":["lunch"],"dinner":["dinner","supper"]}
QUICK_KW=["quick","fast","easy","under 30","under 20","simple"]
def detect_meal(t):
    t=norm(t)
    for m,kws in MEAL_KW.items():
        if any(k in t for k in kws): return m
SUBS={"paneer":["Firm tofu (1:1, vegan)","Halloumi (1:1)","Chicken breast (1:1)"],"chicken":["Turkey (1:1)","Firm tofu (1:1, vegan)","Paneer (1:1, veg)","Chickpeas (1 cup/200g)"],"beef":["Lamb (1:1)","Portobello mushroom (1:1)","Jackfruit (1:1)"],"salmon":["Tuna steak (1:1)","Cod fillet (1:1)","Firm tofu (1:1)"],"fish":["Tofu (1:1)","Jackfruit (1:1)"],"shrimp":["Chicken strips (1:1)","Scallops (1:1)","Tofu (1:1)"],"butter":["Ghee (¾:1)","Coconut oil (¾:1)","Olive oil (¾:1)"],"cream":["Coconut cream (1:1)","Cashew cream (1:1)","Greek yogurt (1:1)"],"eggs":["Flax egg (1tbsp+3tbsp water)","Silken tofu (¼cup/egg)"],"milk":["Oat milk (1:1)","Almond milk (1:1)","Soy milk (1:1)"],"apple":["Pear (1:1)","Peach (1:1)"],"mango":["Peach (1:1)","Papaya (1:1)"],"strawberry":["Raspberries (1:1)","Peach (1:1)"],"yogurt":["Sour cream (1:1)","Coconut yogurt (1:1)"],"pasta":["Zucchini noodles (1:1)","Rice noodles (1:1)"],"rice":["Quinoa (1:1)","Cauliflower rice (1:1)"],"coconut milk":["Cashew cream (1:1)","Heavy cream (1:1)"],"chickpeas":["White beans (1:1)","Lentils (1:1)"],"garlic":["Garlic powder (⅛tsp/clove)"],"carrot":["Parsnip (1:1)","Sweet potato (1:1)"],"cauliflower":["Broccoli (1:1)","Romanesco (1:1)"],"chocolate":["Carob powder (1:1)"],"nuts":["Sunflower seeds (1:1)","Pumpkin seeds (1:1)"]}

R=[
 {"id":"r01","name":"Chicken Biryani","cuisine":"Indian","diet":["non-veg"],"time":"60 min","servings":4,"tags":["rice","main","dinner","spicy","chicken"],"ingredients":{"chicken":"500g","basmati rice":"2 cups","onion":"3","tomato":"2","yogurt":"1 cup","garlic":"6 cloves","ginger":"2 inch","biryani masala":"3 tbsp","ghee":"3 tbsp","mint":"handful","saffron":"pinch"},"steps":["Marinate chicken with yogurt, spices, ginger-garlic 2 hours.","Parboil basmati rice 70% with whole spices.","Fry onions in ghee until golden brown.","Cook chicken with tomatoes until oil separates.","Layer rice over chicken, top with saffron milk and fried onions. Dum cook 25 min."]},
 {"id":"r02","name":"Butter Chicken","cuisine":"Indian","diet":["non-veg"],"time":"45 min","servings":4,"tags":["curry","main","dinner","mild","chicken"],"ingredients":{"chicken":"600g","butter":"4 tbsp","cream":"½ cup","tomato puree":"1 cup","onion":"2","garlic":"6 cloves","ginger":"1 inch","garam masala":"1 tsp","chili":"2 tsp"},"steps":["Marinate and grill chicken until charred.","Sauté onion-garlic-ginger in butter, add tomato puree, simmer 15 min.","Blend sauce smooth.","Add grilled chicken and cream, simmer 10 min.","Finish with butter and fenugreek. Serve with naan."]},
 {"id":"r03","name":"Thai Green Curry","cuisine":"Thai","diet":["non-veg"],"time":"30 min","servings":4,"tags":["curry","main","dinner","chicken","coconut","quick"],"ingredients":{"chicken":"400g","coconut milk":"400ml","green curry paste":"3 tbsp","bell pepper":"1","fish sauce":"2 tbsp","basil":"handful","zucchini":"1","oil":"1 tbsp"},"steps":["Fry curry paste in oil 1 min.","Add coconut milk, simmer.","Add chicken, cook through.","Add vegetables and fish sauce.","Finish with basil. Serve with jasmine rice."]},
 {"id":"r04","name":"Chicken Caesar Salad","cuisine":"American","diet":["non-veg"],"time":"25 min","servings":2,"tags":["salad","lunch","quick","chicken"],"ingredients":{"chicken":"2 breasts","romaine lettuce":"1 head","parmesan":"50g","bread":"1 cup croutons","yogurt":"4 tbsp","lemon":"1","olive oil":"2 tbsp"},"steps":["Grill chicken 6 min per side, rest 5 min, slice.","Toss romaine with caesar dressing.","Top with chicken, croutons, parmesan.","Finish with lemon and cracked pepper."]},
 {"id":"r05","name":"Chicken Soup","cuisine":"American","diet":["non-veg"],"time":"50 min","servings":6,"tags":["soup","lunch","dinner","healthy","chicken"],"ingredients":{"chicken":"500g","carrot":"3","celery":"3 stalks","onion":"1","garlic":"4 cloves","chicken broth":"6 cups","pasta":"200g noodles","thyme":"4 sprigs"},"steps":["Simmer chicken in broth with thyme 30 min.","Remove and shred chicken.","Sauté onion, celery, carrot.","Return broth, chicken; add noodles.","Cook 8 min. Season and serve."]},
 {"id":"r06","name":"Chicken Fried Rice","cuisine":"Chinese","diet":["non-veg"],"time":"20 min","servings":3,"tags":["rice","main","dinner","lunch","chicken","quick"],"ingredients":{"chicken":"300g","rice":"3 cups cooked","eggs":"2","soy sauce":"3 tbsp","garlic":"3 cloves","spring onion":"4","sesame oil":"1 tsp","oil":"2 tbsp"},"steps":["Cook diced chicken in wok until golden.","Scramble eggs, push aside.","Add garlic and rice, stir-fry 3 min.","Season with soy sauce.","Finish with sesame oil and spring onion."]},
 {"id":"r07","name":"Grilled Salmon","cuisine":"Mediterranean","diet":["non-veg","pescatarian"],"time":"20 min","servings":4,"tags":["seafood","dinner","quick","healthy","fish","salmon"],"ingredients":{"salmon":"4 fillets","butter":"3 tbsp","lemon":"2","garlic":"3 cloves","dill":"handful","olive oil":"2 tbsp"},"steps":["Pat salmon dry, season well.","Grill 4 min per side on oiled pan.","Melt butter, add garlic 1 min.","Add lemon juice and dill.","Spoon sauce generously over salmon."]},
 {"id":"r08","name":"Prawn Stir-Fry","cuisine":"Chinese","diet":["non-veg","pescatarian"],"time":"15 min","servings":3,"tags":["seafood","dinner","quick","prawn","shrimp"],"ingredients":{"shrimp":"400g prawns","bell pepper":"2","garlic":"4 cloves","ginger":"1 inch","soy sauce":"3 tbsp","sesame oil":"1 tsp","spring onion":"4","oil":"2 tbsp","chili":"1 tsp"},"steps":["Heat wok smoking hot. Add oil, garlic, ginger 30 sec.","Add prawns, cook 2 min until pink.","Add bell peppers, stir-fry 2 min.","Add soy sauce and chili.","Finish with sesame oil and spring onion."]},
 {"id":"r09","name":"Garlic Butter Shrimp Pasta","cuisine":"Italian","diet":["non-veg","pescatarian"],"time":"25 min","servings":4,"tags":["pasta","seafood","dinner","quick","shrimp","prawn"],"ingredients":{"shrimp":"400g","pasta":"400g","butter":"4 tbsp","garlic":"6 cloves","lemon":"1","parmesan":"60g","olive oil":"2 tbsp","chili":"pinch","basil":"handful"},"steps":["Boil pasta al dente, save pasta water.","Cook garlic in butter+oil 1 min.","Add shrimp, cook 2 min per side.","Add lemon juice and chili flakes.","Toss with pasta and parmesan. Top with basil."]},
 {"id":"r10","name":"Fish Tacos","cuisine":"Mexican","diet":["non-veg","pescatarian"],"time":"25 min","servings":4,"tags":["seafood","lunch","quick","fish"],"ingredients":{"fish":"500g white fish","taco shells":"8","yogurt":"½ cup","lime":"2","cabbage":"1 cup shredded","garlic":"2 cloves","cumin":"1 tsp","chili":"1 tsp","olive oil":"2 tbsp","cilantro":"handful"},"steps":["Season fish, pan-fry 3 min per side.","Mix yogurt with lime juice for crema.","Warm taco shells.","Fill with fish, cabbage, and crema.","Top with cilantro and lime."]},
 {"id":"r11","name":"Tuna Pasta Salad","cuisine":"Western","diet":["non-veg","pescatarian"],"time":"20 min","servings":4,"tags":["salad","pasta","seafood","lunch","quick","tuna"],"ingredients":{"tuna":"2 cans","pasta":"300g","celery":"3 stalks","onion":"½","lemon":"1","yogurt":"4 tbsp mayo","salt":"to taste","black pepper":"to taste"},"steps":["Cook pasta, cool under cold water.","Flake tuna, dice celery and onion.","Mix mayo with lemon for dressing.","Combine pasta, tuna, vegetables.","Fold in dressing. Chill before serving."]},
 {"id":"r12","name":"Prawn Curry","cuisine":"Indian","diet":["non-veg","pescatarian"],"time":"35 min","servings":4,"tags":["curry","seafood","dinner","spicy","prawn","shrimp"],"ingredients":{"shrimp":"500g prawns","coconut milk":"400ml","onion":"2","tomato":"3","garlic":"5 cloves","ginger":"1 inch","turmeric":"1 tsp","chili":"2 tsp","cumin":"1 tsp","coriander powder":"2 tsp","oil":"3 tbsp"},"steps":["Sauté onion golden. Add ginger-garlic.","Add tomatoes and all spices. Cook until oil separates.","Pour coconut milk, simmer 5 min.","Add prawns, cook 4-5 min until pink.","Garnish with cilantro. Serve with rice."]},
 {"id":"r13","name":"Baked Cod with Herbs","cuisine":"Mediterranean","diet":["non-veg","pescatarian"],"time":"30 min","servings":4,"tags":["seafood","dinner","healthy","fish","cod"],"ingredients":{"cod":"4 fillets","olive oil":"3 tbsp","garlic":"4 cloves","lemon":"1","thyme":"4 sprigs","rosemary":"2 sprigs","tomato":"2","salt":"to taste","black pepper":"to taste"},"steps":["Preheat oven 200°C. Place cod in dish.","Drizzle with olive oil.","Top with garlic, herbs, tomatoes.","Squeeze lemon, season.","Bake 15-18 min until fish flakes easily."]},
 {"id":"r14","name":"Salmon Fried Rice","cuisine":"Asian","diet":["non-veg","pescatarian"],"time":"20 min","servings":3,"tags":["rice","seafood","dinner","quick","salmon","fish"],"ingredients":{"salmon":"300g","rice":"3 cups cooked","eggs":"2","soy sauce":"3 tbsp","garlic":"3 cloves","ginger":"1 inch","sesame oil":"1 tsp","spring onion":"4","oil":"2 tbsp"},"steps":["Cook salmon, flake into chunks.","Scramble eggs in wok, push aside.","Add garlic, ginger, then rice. Stir-fry 3 min.","Add soy sauce.","Fold in salmon. Finish with sesame oil."]},
 {"id":"r15","name":"Palak Paneer","cuisine":"Indian","diet":["vegetarian"],"time":"30 min","servings":3,"tags":["curry","vegetarian","dinner","main","paneer","quick"],"ingredients":{"paneer":"250g","spinach":"500g","onion":"2","tomato":"1","garlic":"4 cloves","ginger":"1 inch","cream":"2 tbsp","cumin":"1 tsp","garam masala":"½ tsp","butter":"2 tbsp"},"steps":["Blanch spinach 2 min, blend smooth.","Sauté cumin in butter, add onion golden.","Add ginger-garlic, tomato, cook down.","Pour spinach puree, simmer 5 min.","Add paneer, cream, garam masala."]},
 {"id":"r16","name":"Paneer Tikka Masala","cuisine":"Indian","diet":["vegetarian"],"time":"50 min","servings":4,"tags":["curry","vegetarian","dinner","main","paneer"],"ingredients":{"paneer":"300g","yogurt":"½ cup","bell pepper":"2","onion":"2","tomato":"3","cream":"¼ cup","garam masala":"1.5 tsp","chili":"1.5 tsp","garlic":"5 cloves","butter":"2 tbsp"},"steps":["Marinate paneer in yogurt and spices 30 min.","Grill paneer and peppers until charred.","Build masala: onion, garlic, tomatoes, spices.","Blend sauce smooth, add cream and paneer.","Simmer 10 min. Serve with roti."]},
 {"id":"r17","name":"Chana Masala","cuisine":"Indian","diet":["vegetarian","vegan"],"time":"40 min","servings":4,"tags":["curry","vegan","dinner","main"],"ingredients":{"chickpeas":"2 cans","onion":"2","tomato":"3","garlic":"5 cloves","ginger":"1 inch","cumin":"1 tsp","coriander powder":"2 tsp","chana masala":"2 tsp","oil":"3 tbsp"},"steps":["Sauté cumin and onion golden.","Add ginger-garlic, tomatoes, cook until oil separates.","Add spices and chickpeas.","Simmer 20 min.","Mash some chickpeas to thicken."]},
 {"id":"r18","name":"Dal Makhani","cuisine":"Indian","diet":["vegetarian"],"time":"90 min","servings":4,"tags":["lentils","vegetarian","dinner","main","comfort"],"ingredients":{"lentils":"1 cup black","kidney beans":"¼ cup","butter":"3 tbsp","cream":"¼ cup","tomato puree":"1 cup","onion":"2","garlic":"5 cloves","garam masala":"1 tsp"},"steps":["Soak and pressure cook lentils+beans 45 min.","Sauté onion golden, add garlic, spices, tomato puree.","Combine lentils with masala, simmer 20 min.","Add cream and butter, slow cook 10 min.","Serve with naan."]},
 {"id":"r19","name":"Mushroom Risotto","cuisine":"Italian","diet":["vegetarian"],"time":"35 min","servings":4,"tags":["rice","vegetarian","dinner","main","mushroom"],"ingredients":{"mushroom":"300g","rice":"1.5 cups arborio","onion":"1","garlic":"3 cloves","white wine":"½ cup","parmesan":"80g","butter":"4 tbsp","vegetable stock":"5 cups"},"steps":["Keep stock warm.","Sauté mushrooms golden; set aside.","Cook onion+garlic in butter, add rice, toast 1 min.","Add wine then stock ladle by ladle, stirring.","Fold in mushrooms, parmesan, butter after 18 min."]},
 {"id":"r20","name":"Shakshuka","cuisine":"Middle Eastern","diet":["vegetarian"],"time":"30 min","servings":3,"tags":["breakfast","egg","vegetarian","quick"],"ingredients":{"eggs":"4","tomato":"400g canned","bell pepper":"1","onion":"1","garlic":"4 cloves","cumin":"1 tsp","paprika":"1 tsp","olive oil":"2 tbsp"},"steps":["Sauté onion and pepper in olive oil.","Add garlic and spices, cook 1 min.","Pour tomatoes, simmer 10 min.","Make 4 wells, crack in eggs, cover 5-8 min.","Serve with crusty bread."]},
 {"id":"r21","name":"Avocado Toast","cuisine":"Western","diet":["vegetarian"],"time":"10 min","servings":2,"tags":["breakfast","quick","healthy","vegetarian"],"ingredients":{"avocado":"1","bread":"2 slices","eggs":"2","lemon":"½","chili":"pinch"},"steps":["Toast bread until golden.","Mash avocado with lemon, salt, pepper.","Poach eggs 3 min.","Spread avocado on toast.","Top with egg and chili flakes."]},
 {"id":"r22","name":"Pesto Pasta","cuisine":"Italian","diet":["vegetarian"],"time":"20 min","servings":4,"tags":["pasta","lunch","dinner","quick","vegetarian"],"ingredients":{"pasta":"400g","basil":"2 cups","nuts":"3 tbsp pine","parmesan":"60g","garlic":"2 cloves","olive oil":"½ cup"},"steps":["Boil pasta al dente, save pasta water.","Blend basil, pine nuts, garlic, parmesan.","Drizzle oil while blending.","Toss pasta with pesto.","Loosen with pasta water."]},
 {"id":"r23","name":"Margherita Pizza","cuisine":"Italian","diet":["vegetarian"],"time":"25 min","servings":2,"tags":["main","dinner","baked","vegetarian"],"ingredients":{"pizza dough":"300g","tomato sauce":"½ cup","cheese":"200g mozzarella","basil":"handful","olive oil":"2 tbsp"},"steps":["Preheat oven 250°C with stone.","Stretch dough to 30cm circle.","Spread tomato sauce, add mozzarella.","Drizzle olive oil.","Bake 10-12 min. Top with fresh basil."]},
 {"id":"r24","name":"Vegetable Fried Rice","cuisine":"Chinese","diet":["vegetarian","vegan"],"time":"20 min","servings":3,"tags":["rice","lunch","dinner","vegan","quick","vegetarian"],"ingredients":{"rice":"3 cups cooked","eggs":"3","carrot":"1","peas":"½ cup","spring onion":"4","soy sauce":"3 tbsp","garlic":"3 cloves","sesame oil":"1 tsp"},"steps":["Heat wok smoking hot.","Scramble eggs, push aside.","Add garlic, carrot, peas.","Add rice, stir-fry breaking clumps.","Season with soy sauce. Finish with sesame oil."]},
 {"id":"r25","name":"Egg Fried Rice","cuisine":"Chinese","diet":["vegetarian"],"time":"15 min","servings":2,"tags":["breakfast","rice","quick","egg","vegetarian"],"ingredients":{"rice":"2 cups cooked","eggs":"3","soy sauce":"2 tbsp","garlic":"2 cloves","spring onion":"3","sesame oil":"1 tsp","oil":"1 tbsp"},"steps":["Heat oil in wok on high.","Scramble eggs until just set.","Add garlic and rice, stir-fry 3 min.","Add soy sauce, toss.","Finish with sesame oil and spring onion."]},
 {"id":"r26","name":"Masala Omelette","cuisine":"Indian","diet":["vegetarian"],"time":"10 min","servings":1,"tags":["breakfast","quick","egg","vegetarian"],"ingredients":{"eggs":"3","onion":"1 small","tomato":"1 small","chili":"1","cilantro":"handful","turmeric":"pinch","oil":"1 tsp"},"steps":["Beat eggs with salt and turmeric.","Add onion, tomato, chili, cilantro.","Heat oil in non-stick pan.","Pour mixture, cook on medium.","Fold in half. Serve hot."]},
 {"id":"r27","name":"Spaghetti Carbonara","cuisine":"Italian","diet":["non-veg"],"time":"25 min","servings":4,"tags":["pasta","dinner","quick","main","pork"],"ingredients":{"pasta":"400g spaghetti","pork":"150g pancetta","eggs":"4","parmesan":"100g","garlic":"2 cloves","black pepper":"2 tsp"},"steps":["Boil spaghetti al dente, save pasta water.","Fry pancetta and garlic until crispy.","Whisk eggs with parmesan and pepper.","Off heat toss pasta with pancetta then egg mix.","Add pasta water to loosen."]},
 {"id":"r28","name":"Beef Tacos","cuisine":"Mexican","diet":["non-veg"],"time":"25 min","servings":4,"tags":["main","dinner","lunch","quick","beef"],"ingredients":{"beef":"500g ground","taco shells":"8","onion":"1","garlic":"3 cloves","cumin":"1 tsp","chili":"1.5 tsp","tomato":"2","cheese":"100g cheddar","yogurt":"4 tbsp sour cream","lime":"1"},"steps":["Brown beef with onion and garlic.","Add cumin, chili, salt.","Warm taco shells 3 min.","Fill shells with beef, tomato, cheese, sour cream.","Squeeze lime and serve."]},
 {"id":"r29","name":"Tomato Soup","cuisine":"Western","diet":["vegetarian","vegan"],"time":"30 min","servings":4,"tags":["soup","lunch","dinner","vegan","comfort","tomato"],"ingredients":{"tomato":"8 large","onion":"1","garlic":"4 cloves","vegetable stock":"2 cups","olive oil":"2 tbsp","basil":"handful","sugar":"1 tsp"},"steps":["Roast tomatoes and garlic 200°C 20 min.","Sauté onion until soft.","Add roasted tomatoes and stock, simmer 10 min.","Blend smooth.","Season, garnish with basil."]},
 {"id":"r30","name":"Apple Crumble","cuisine":"British","diet":["vegetarian"],"time":"45 min","servings":6,"tags":["dessert","baked","sweet","apple"],"ingredients":{"apple":"4 large","sugar":"4 tbsp","cinnamon":"1 tsp","lemon":"1","flour":"1 cup","butter":"80g cold","oats":"½ cup"},"steps":["Slice apples, toss with sugar, cinnamon, lemon.","Spread in baking dish.","Rub cold butter into flour, oats, sugar until crumbly.","Spread over apples.","Bake 180°C 30 min until golden."]},
 {"id":"r31","name":"Apple Cinnamon Pancakes","cuisine":"American","diet":["vegetarian"],"time":"25 min","servings":4,"tags":["breakfast","sweet","quick","apple","dessert"],"ingredients":{"apple":"2","flour":"1.5 cups","eggs":"2","milk":"1 cup","sugar":"2 tbsp","cinnamon":"1 tsp","baking powder":"2 tsp","butter":"2 tbsp","vanilla extract":"1 tsp"},"steps":["Grate apple. Mix dry ingredients.","Whisk eggs, milk, vanilla, melted butter.","Fold wet into dry, add grated apple.","Cook pancakes 2-3 min per side.","Serve with maple syrup."]},
 {"id":"r32","name":"Strawberry Cheesecake","cuisine":"American","diet":["vegetarian"],"time":"60 min","servings":8,"tags":["dessert","sweet","no-bake","strawberry","cheesecake"],"ingredients":{"strawberry":"300g","cream cheese":"400g","cream":"200ml whipping","wafers":"200g","butter":"80g","sugar":"100g","lemon":"1","vanilla extract":"1 tsp"},"steps":["Crush biscuits+butter, press into tin. Chill 30 min.","Beat cream cheese with sugar, vanilla, lemon.","Whip cream to soft peaks, fold in.","Spread over base. Chill 4+ hours.","Top with sliced strawberries."]},
 {"id":"r33","name":"Strawberry Smoothie","cuisine":"Western","diet":["vegetarian","vegan"],"time":"5 min","servings":2,"tags":["drink","healthy","quick","strawberry","dessert"],"ingredients":{"strawberry":"2 cups","banana":"1","milk":"1 cup","honey":"1 tbsp","vanilla extract":"½ tsp"},"steps":["Hull strawberries.","Add all ingredients to blender.","Blend on high 60 sec.","Adjust sweetness.","Serve chilled."]},
 {"id":"r34","name":"Strawberry Shortcake","cuisine":"American","diet":["vegetarian"],"time":"40 min","servings":8,"tags":["dessert","baked","sweet","strawberry"],"ingredients":{"strawberry":"400g","flour":"2 cups","sugar":"7 tbsp","baking powder":"1 tbsp","butter":"6 tbsp cold","cream":"1 cup","vanilla extract":"1 tsp"},"steps":["Macerate strawberries with 3 tbsp sugar 30 min.","Mix flour, 4 tbsp sugar, baking powder; cut in butter.","Add cream and vanilla; mix until just combined.","Bake 200°C 15 min until golden.","Fill biscuits with strawberries and whipped cream."]},
 {"id":"r35","name":"Carrot Cake","cuisine":"American","diet":["vegetarian"],"time":"60 min","servings":12,"tags":["dessert","baked","sweet","carrot"],"ingredients":{"carrot":"3 cups grated","flour":"2 cups","sugar":"1.5 cups","eggs":"4","oil":"1 cup","cinnamon":"2 tsp","baking soda":"2 tsp","vanilla extract":"1 tsp","cream cheese":"400g","butter":"100g"},"steps":["Preheat 180°C. Mix dry ingredients.","Whisk eggs, oil, sugar, vanilla.","Fold wet into dry, add grated carrot.","Bake 30-35 min.","Beat cream cheese+butter for frosting. Frost cooled cake."]},
 {"id":"r36","name":"Carrot Halwa","cuisine":"Indian","diet":["vegetarian"],"time":"45 min","servings":6,"tags":["dessert","sweet","indian","carrot"],"ingredients":{"carrot":"500g grated","milk":"2 cups","sugar":"½ cup","ghee":"3 tbsp","cardamom":"4 pods","nuts":"handful"},"steps":["Cook grated carrot with milk, stirring, until milk evaporates 20-25 min.","Add ghee, cook 5 min.","Add sugar, cook 10 min until halwa leaves pan sides.","Add cardamom and nuts.","Serve warm."]},
 {"id":"r37","name":"Banana Pancakes","cuisine":"American","diet":["vegetarian"],"time":"15 min","servings":2,"tags":["breakfast","sweet","quick","banana","dessert"],"ingredients":{"banana":"2 ripe","oats":"1 cup","eggs":"2","milk":"¼ cup","cinnamon":"½ tsp","baking powder":"1 tsp","vanilla extract":"½ tsp"},"steps":["Mash very ripe bananas.","Blend oats to flour.","Mix wet and dry; add oat flour.","Cook small pancakes 2 min per side.","Serve with honey."]},
 {"id":"r38","name":"Mango Lassi","cuisine":"Indian","diet":["vegetarian"],"time":"5 min","servings":2,"tags":["drink","sweet","quick","mango","dessert"],"ingredients":{"mango":"2 ripe","yogurt":"1 cup","milk":"½ cup","sugar":"2 tbsp","cardamom":"pinch"},"steps":["Add mango and yogurt to blender.","Add milk, sugar, cardamom.","Blend 60 sec.","Adjust sweetness.","Serve chilled."]},
 {"id":"r39","name":"Apple Smoothie","cuisine":"Western","diet":["vegetarian","vegan"],"time":"5 min","servings":2,"tags":["drink","healthy","quick","apple","breakfast"],"ingredients":{"apple":"2","banana":"1","milk":"1 cup","honey":"1 tbsp","cinnamon":"pinch"},"steps":["Chop apple.","Add all to blender.","Blend until smooth.","Adjust honey.","Serve immediately."]},
 {"id":"r40","name":"Apple Sundae","cuisine":"American","diet":["vegetarian"],"time":"10 min","servings":2,"tags":["dessert","sweet","quick","apple"],"ingredients":{"apple":"1","vanilla ice cream":"3 scoops","caramel sauce":"2 tbsp","whipped cream":"¼ cup","cinnamon":"pinch","butter":"1 tbsp"},"steps":["Slice apple, sauté in butter 3 min.","Scoop ice cream into bowl.","Top with warm caramel apple slices.","Add whipped cream.","Dust with cinnamon."]},
 {"id":"r41","name":"Strawberry Ice Cream","cuisine":"American","diet":["vegetarian"],"time":"10 min + freeze","servings":6,"tags":["dessert","sweet","frozen","strawberry"],"ingredients":{"strawberry":"400g","cream":"400ml whipping","milk":"200ml","sugar":"100g","vanilla extract":"1 tsp"},"steps":["Blend strawberries with sugar.","Whip cream to soft peaks.","Fold in strawberry puree, milk, vanilla.","Freeze 6 hours, stirring every 2 hours.","Scoop and serve."]},
 {"id":"r42","name":"Chocolate Cake","cuisine":"American","diet":["vegetarian"],"time":"50 min","servings":12,"tags":["dessert","baked","sweet","chocolate"],"ingredients":{"flour":"2 cups","cocoa powder":"¾ cup","sugar":"2 cups","eggs":"3","milk":"1 cup","oil":"½ cup","baking powder":"2 tsp","baking soda":"1 tsp","vanilla extract":"1 tsp","butter":"100g"},"steps":["Sift flour, cocoa, baking powder, baking soda.","Whisk eggs, milk, oil, vanilla.","Fold wet into dry.","Bake 180°C 32-35 min.","Frost with chocolate buttercream."]},
 {"id":"r43","name":"Classic Omelette","cuisine":"French","diet":["vegetarian"],"time":"5 min","servings":1,"tags":["breakfast","quick","egg","vegetarian"],"ingredients":{"eggs":"3","butter":"1 tbsp","salt":"pinch","black pepper":"pinch"},"steps":["Beat eggs with salt and pepper.","Heat butter until foamy.","Pour eggs, stir gently while shaking pan.","Fold when edges set but center still soft.","Slide out immediately onto warm plate."]},
 {"id":"r44","name":"Banana Oat Smoothie","cuisine":"Western","diet":["vegetarian","vegan"],"time":"5 min","servings":2,"tags":["drink","healthy","breakfast","quick","banana"],"ingredients":{"banana":"2","oats":"½ cup","milk":"1.5 cups","honey":"1 tbsp","cinnamon":"pinch","vanilla extract":"½ tsp"},"steps":["Combine oats and half milk, blend 30 sec.","Add banana, remaining milk, honey, vanilla, cinnamon.","Blend 60 sec until smooth.","Adjust sweetness.","Serve immediately."]},
 {"id":"r45","name":"Lamb Rogan Josh","cuisine":"Indian","diet":["non-veg"],"time":"70 min","servings":4,"tags":["curry","main","dinner","spicy","lamb"],"ingredients":{"lamb":"600g","onion":"3","tomato":"2","yogurt":"1 cup","garlic":"6 cloves","ginger":"2 inch","garam masala":"2 tsp","chili":"2 tsp","oil":"4 tbsp","cardamom":"4 pods"},"steps":["Brown lamb in batches.","Cook onion until dark golden.","Add garlic-ginger, tomatoes, spices, yogurt.","Return lamb, add 1 cup water.","Simmer covered 45 min until tender."]},
 {"id":"r46","name":"Greek Salad","cuisine":"Mediterranean","diet":["vegetarian"],"time":"10 min","servings":4,"tags":["salad","lunch","quick","healthy","vegetarian"],"ingredients":{"tomato":"4","cucumber":"1","onion":"1 red","cheese":"150g feta","olive oil":"3 tbsp","lemon":"1","oregano":"1 tsp","salt":"to taste"},"steps":["Chop tomatoes, cucumber, red onion roughly.","Place in bowl.","Crumble feta over top.","Drizzle olive oil and lemon.","Season with oregano, salt, pepper."]},
 {"id":"r47","name":"Caprese Salad","cuisine":"Italian","diet":["vegetarian"],"time":"10 min","servings":4,"tags":["salad","lunch","quick","vegetarian"],"ingredients":{"tomato":"4 large","cheese":"300g fresh mozzarella","basil":"handful","olive oil":"3 tbsp","salt":"to taste","black pepper":"to taste"},"steps":["Slice tomatoes and mozzarella.","Alternate on platter.","Tuck basil between slices.","Drizzle olive oil.","Season with flaky salt and pepper."]},
 {"id":"r48","name":"Red Lentil Soup","cuisine":"Middle Eastern","diet":["vegetarian","vegan"],"time":"35 min","servings":4,"tags":["soup","lunch","dinner","vegan","healthy","lentil"],"ingredients":{"lentils":"1.5 cups red","onion":"2","garlic":"4 cloves","tomato":"2","cumin":"1.5 tsp","turmeric":"1 tsp","lemon":"1","olive oil":"3 tbsp","vegetable stock":"6 cups"},"steps":["Sauté onion golden, add garlic.","Add cumin, turmeric, 1 min.","Add tomatoes, lentils, stock.","Simmer 20 min.","Blend half for creamy texture. Add lemon."]},
 {"id":"r49","name":"Vegetable Curry","cuisine":"Indian","diet":["vegetarian","vegan"],"time":"35 min","servings":4,"tags":["curry","dinner","vegan","main","vegetarian"],"ingredients":{"potato":"3","carrot":"2","peas":"1 cup","onion":"2","tomato":"3","garlic":"4 cloves","ginger":"1 inch","cumin":"1 tsp","turmeric":"1 tsp","garam masala":"1 tsp","oil":"3 tbsp","coconut milk":"200ml"},"steps":["Sauté onion, garlic, ginger.","Add spices, tomatoes, cook 10 min.","Add potatoes, carrots, 1 cup water. Simmer 15 min.","Add peas and coconut milk, simmer 5 min.","Garnish with cilantro."]},
 {"id":"r50","name":"Stuffed Bell Peppers","cuisine":"Mediterranean","diet":["vegetarian"],"time":"45 min","servings":4,"tags":["main","dinner","baked","vegetarian"],"ingredients":{"bell pepper":"4 large","rice":"1 cup cooked","cheese":"100g feta","tomato":"2","onion":"1","garlic":"3 cloves","olive oil":"2 tbsp","oregano":"1 tsp","basil":"handful"},"steps":["Preheat 180°C. Slice tops off peppers, remove seeds.","Sauté onion and garlic in olive oil.","Mix rice, feta, tomatoes, herbs with onion.","Fill peppers tightly.","Bake 30 min until tender."]},
 {"id":"r51","name":"Cauliflower Soup","cuisine":"Western","diet":["vegetarian","vegan"],"time":"30 min","servings":4,"tags":["soup","healthy","vegetarian","vegan","cauliflower"],"ingredients":{"cauliflower":"1 head","onion":"1","garlic":"4 cloves","vegetable stock":"4 cups","olive oil":"2 tbsp","cream":"4 tbsp","black pepper":"to taste","thyme":"3 sprigs"},"steps":["Sauté onion in oil 5 min, add garlic.","Add cauliflower and thyme.","Add stock. Simmer 20 min.","Blend completely smooth.","Stir in cream. Season."]},
 {"id":"r52","name":"Aloo Gobi","cuisine":"Indian","diet":["vegetarian","vegan"],"time":"30 min","servings":4,"tags":["curry","vegetarian","vegan","cauliflower","potato","quick"],"ingredients":{"cauliflower":"1 head","potato":"3","onion":"1","tomato":"2","garlic":"3 cloves","ginger":"1 inch","turmeric":"1 tsp","cumin":"1 tsp","chili":"1 tsp","coriander powder":"2 tsp","oil":"3 tbsp","cilantro":"handful"},"steps":["Heat oil, add cumin, let splutter.","Add onion golden, add ginger-garlic.","Add tomatoes and spices, cook 5 min.","Add potato and cauliflower, cover, cook 15-18 min.","Garnish with cilantro."]},
 {"id":"r53","name":"Roasted Cauliflower","cuisine":"Mediterranean","diet":["vegetarian","vegan"],"time":"35 min","servings":4,"tags":["side","healthy","vegetarian","vegan","cauliflower"],"ingredients":{"cauliflower":"1 head","olive oil":"3 tbsp","garlic":"4 cloves","lemon":"1","paprika":"1 tsp","cumin":"1 tsp","salt":"to taste","black pepper":"to taste","cilantro":"handful"},"steps":["Preheat oven 220°C. Cut cauliflower into florets.","Toss with oil, garlic, paprika, cumin, salt, pepper.","Spread on baking sheet — don't crowd.","Roast 25-30 min, tossing halfway.","Squeeze lemon, top with cilantro."]},
]
for r in R: r["_ci"]={canon(norm(k)) for k in r.get("ingredients",{})}; r["_sf"]=bool(r["_ci"]&SEAFOOD)

SESSIONS:dict[str,dict]={}
def get_sess(sid):
    if sid not in SESSIONS: SESSIONS[sid]={"exclude":[],"diet":[],"history":[],"pending_gen":None}
    return SESSIONS[sid]

_col=None;_emb=None
def get_chroma():
    global _col,_emb
    if _col: return _col
    try:
        import chromadb; from sentence_transformers import SentenceTransformer
        client=chromadb.PersistentClient(path=CHROMA_DIR); col=client.get_or_create_collection("rv6",metadata={"hnsw:space":"cosine"})
        dh=hashlib.md5(json.dumps([r["id"] for r in R]).encode()).hexdigest(); fresh=False
        if col.count()>0:
            try: fresh=col.get(ids=["__m__"],include=["metadatas"])["metadatas"][0].get("h")==dh
            except: pass
        if not fresh:
            log.info("🔧 Embedding recipes…"); mdl=SentenceTransformer(EMBED_MDL); _emb=mdl
            texts=[f"{r['name']} {r['cuisine']} {' '.join(r.get('tags',[]))} {' '.join(r.get('ingredients',{}).keys())}" for r in R]
            embs=mdl.encode(texts,normalize_embeddings=True).tolist()
            col.upsert(documents=texts,embeddings=embs,ids=[r["id"] for r in R],metadatas=[{"n":r["name"]} for r in R])
            col.upsert(documents=["m"],ids=["__m__"],metadatas=[{"h":dh}]); log.info("✅ Embeddings persisted.")
        else: log.info("✅ Cached embeddings loaded."); _emb=SentenceTransformer(EMBED_MDL)
        _col=col; return col
    except Exception as e: log.warning(f"ChromaDB: {e}"); return None

def ss(q):
    c=get_chroma()
    if not c or not _emb: return {}
    try:
        qe=_emb.encode([q],normalize_embeddings=True).tolist(); r=c.query(query_embeddings=qe,n_results=min(len(R),55),where={"n":{"$ne":"__m__"}})
        return {rid:1.0-d for rid,d in zip(r["ids"][0],r["distances"][0])}
    except: return {}

NOISE={"i","have","want","make","cook","need","some","the","and","with","for","a","an","me","please","can","my","is","no","any","all","do","what","give","suggest","show","recipes","recipe","dish","food","using","would","like","also","but","not","only","just","something","cup","cups","tbsp","tsp","grams","kg","ml","few","bit","little","help","hello","hi","hey","ok","yes","yeah","thanks","great","awesome","random","list","dishes","get","find","search","quick","easy","simple","spicy","healthy","veg","non","vegetarian","vegan"}
_TOKS=sorted({norm(v) for vs in IM.values() for v in vs}|{norm(k) for r in R for k in r.get("ingredients",{})},key=len,reverse=True)
def extract_ings(text):
    t=norm(text); found=[]
    for tok in _TOKS:
        if re.search(r'(?<![a-z])'+re.escape(tok)+r'(?![a-z])',t): found.append(tok); t=re.sub(r'(?<![a-z])'+re.escape(tok)+r'(?![a-z])'," "*len(tok),t)
    for part in re.split(r'[,&]|\band\b',re.sub(r'[^a-z,& \-]+'," ",t)):
        p=part.strip()
        if p and len(p)>2 and p not in NOISE and not p.isdigit(): found.append(p)
    seen,out=set(),[]
    for f in found:
        c=canon(f)
        if c and c not in seen: seen.add(c); out.append(c)
    return out

async def _groq(msgs,max_tokens=400,temp=0.0):
    async with httpx.AsyncClient(timeout=20) as c:
        r=await c.post(GROQ_URL,headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},json={"model":GROQ_MDL,"messages":msgs,"max_tokens":max_tokens,"temperature":temp})
        r.raise_for_status(); return r.json()["choices"][0]["message"]["content"].strip()

NLU_SYS="""Extract intent from user message. Return ONLY valid JSON:
{"intent":"find_recipe|substitution|set_preference|override_preference|confirm_gen|decline_gen|random_recipe|greeting|help|thanks","ingredients":[],"exclude":[],"diet":[],"meal_type":null,"cuisine":null,"query_for_search":""}
Rules: "no X"→exclude+set_preference | "include X"→override_preference | "reset preferences"→override_preference,ingredients:["__reset__"] | "yes/sure/ok/generate"→confirm_gen | "no/skip"→decline_gen | "random/surprise"→random_recipe | "veg/vegetarian"→diet:["vegetarian"] | "non-veg/nonveg/meat"→diet:["non-veg"] | "vegan"→diet:["vegan"] | meal_type:breakfast|lunch|dinner|dessert|drink|snack|soup|salad"""

async def groq_nlu(text,history):
    msgs=[{"role":"system","content":NLU_SYS}]+[{"role":h["role"],"content":h["content"]} for h in history[-4:]]+[{"role":"user","content":text}]
    try:
        raw=await _groq(msgs,max_tokens=250); raw=re.sub(r"^```json|^```|```$","",raw,flags=re.MULTILINE).strip(); return json.loads(raw)
    except Exception as e: log.warning(f"NLU fallback:{e}"); return _rule_nlu(text)

def _rule_nlu(text):
    t=norm(text); intent="find_recipe"
    if re.search(r"^(hi|hello|hey)\b",t): intent="greeting"
    elif re.search(r"\b(help|what can you)\b",t): intent="help"
    elif re.search(r"\b(thank|awesome|great)\b",t): intent="thanks"
    elif re.search(r"\b(substitute|replace|instead of|alternative)\b",t): intent="substitution"
    elif re.search(r"\b(reset|clear|forget).*(prefer|exclude)\b|\breset preferences\b",t): return {"intent":"override_preference","ingredients":["__reset__"],"exclude":[],"diet":[],"meal_type":None,"cuisine":None,"query_for_search":text}
    elif re.search(r"\b(include|add back)\s+\w",t): intent="override_preference"
    elif re.search(r"\bno\s+\w|\bwithout\s+\w|\bavoid\s+\w|\bdon.?t\s+(eat|want)\s+\w",t) and not re.search(r"\b(recipe|dish|cook)\b",t): intent="set_preference"
    elif re.search(r"\b(random|surprise)\b",t): intent="random_recipe"
    elif re.search(r"^(yes|sure|ok|go ahead|generate|yeah|please)\b",t): intent="confirm_gen"
    elif re.search(r"^(no|no thanks|skip|nope)\b",t): intent="decline_gen"
    excl=[m.group(2) for m in re.finditer(r"\b(no|without|avoid|exclude)\s+(\w+)",t)]
    override=[m.group(2) for m in re.finditer(r"\b(include|add back|use)\s+(\w+)",t)]
    dd,_=detect_diet(t); meal=detect_meal(t); cuisine=next((c for c in ["indian","italian","chinese","thai","mexican","american","mediterranean"] if c in t),None)
    return {"intent":intent,"ingredients":extract_ings(t)+override,"exclude":excl,"diet":dd,"meal_type":meal,"cuisine":cuisine.title() if cuisine else None,"query_for_search":text}

async def groq_rerank(user_ings,query,candidates,sess):
    if len(candidates)<=1: return candidates
    lines="\n".join(f"{i+1}.[{h['recipe']['id']}] {h['recipe']['name']}|diet:{h['recipe']['diet']}|ings:{', '.join(list(h['recipe'].get('ingredients',{}).keys())[:5])}" for i,h in enumerate(candidates[:10]))
    try:
        raw=await _groq([{"role":"user","content":f"Rank recipes for:'{query}'\nUser:{user_ings}\nExclude:{sess.get('exclude',[])}\nDiet:{sess.get('_adf',[])}\n{lines}\nReturn ONLY JSON array of IDs. Excluded MUST NOT be in top result."}],max_tokens=120)
        ids=json.loads(re.sub(r"^```json|^```|```$","",raw,flags=re.MULTILINE).strip()); m={h["recipe"]["id"]:h for h in candidates}
        return [m[i] for i in ids if i in m]+[h for h in candidates if h["recipe"]["id"] not in set(ids)]
    except: return candidates

async def groq_explain(recipe,user_ings,matched):
    try: return await _groq([{"role":"user","content":f"Recipe:{recipe['name']}({recipe['cuisine']},{recipe['time']}). User has:{user_ings}. Matched:{matched}. One warm sentence max 20 words why this is top match."}],max_tokens=60,temp=0.3)
    except: return f"Uses {len(matched)} of your ingredients — {'great' if len(matched)>=3 else 'good'} match!"

async def groq_gen(query,exclude,diet):
    prompt=f'Generate a complete recipe for:"{query}". Excluded:{exclude or "none"}. Diet:{diet or "any"}. Return ONLY valid JSON:{{"name":"..","cuisine":"..","diet":[".."],"time":"30 min","servings":4,"tags":[".."],"ingredients":{{"ing":"amount"}},"steps":["step1","step2","step3","step4","step5"]}}'
    for attempt in range(3):
        try:
            raw=await _groq([{"role":"user","content":prompt}],max_tokens=900,temp=0.5); raw=re.sub(r"^```json|^```|```$","",raw,flags=re.MULTILINE).strip()
            m=re.search(r'\{.*\}',raw,re.DOTALL);
            if m: raw=m.group(0)
            data=json.loads(raw)
            if "name" in data and "ingredients" in data and "steps" in data: return data
        except Exception as e: log.warning(f"Gen {attempt+1}:{e}"); await asyncio.sleep(1) if attempt<2 else None
    return None

def score_r(recipe,user_ings,exclude,ssc,query,meal_type,quick,diet_filter=None):
    rc=recipe["_ci"]; q=norm(query); excl=set(exclude); rdiet=set(recipe.get("diet",[]))
    if diet_filter=="vegetarian" and "vegetarian" not in rdiet and "vegan" not in rdiet: return -1,[],[]
    if diet_filter=="vegan" and "vegan" not in rdiet: return -1,[],[]
    if diet_filter=="non-veg" and "non-veg" not in rdiet: return -1,[],[]
    if diet_filter=="pescatarian" and not(rdiet&{"pescatarian","vegetarian","vegan"}): return -1,[],[]
    for ex in excl:
        if ex in rc or any(len(ex)>3 and(ex in r or r in ex) for r in rc): return -1,[],[]
    if "seafood" in excl and recipe["_sf"]: return -1,[],[]
    for sf in SEAFOOD:
        if sf in excl and(sf in rc or any(sf in r for r in rc)): return -1,[],[]
    tags=set(recipe.get("tags",[])); HARD={"dessert","breakfast","soup","drink","salad"}; mb=0.0
    if meal_type:
        mm=meal_type in tags or any(meal_type in t for t in tags)
        if not mm:
            if meal_type=="dessert" and tags&{"sweet","baked","frozen","no-bake","cheesecake","halwa"}: mm=True
            elif meal_type=="breakfast" and tags&{"egg","quick","sweet"}: mm=True
            elif meal_type in{"lunch","dinner"} and tags&{"main","curry","pasta","rice","soup","salad"}: mm=True
            elif meal_type=="drink" and tags&{"smoothie","lassi","juice"}: mm=True
            elif meal_type=="soup" and "soup" in norm(recipe.get("name","")): mm=True
        if mm: mb=0.30
        elif meal_type in HARD: return -1,[],[]
        else: mb=-0.15
    if quick:
        try:
            if int(re.search(r'(\d+)',recipe.get("time","60")).group(1))>30: return CUTOFF,[],[]
        except: pass
    if not user_ings:
        nw=[w for w in norm(recipe["name"]).split() if len(w)>2]
        kw=sum(1 for w in nw if w in q)/max(len(nw),1); tb=sum(0.12 for t in tags if t in q)
        sb=0.30 if any(s in q for s in SEAFOOD|{"seafood","prawn","shrimp"}) and recipe["_sf"] else 0
        return min(1.0,kw*0.40+tb+ssc.get(recipe["id"],0)*0.20+sb+mb),[],[]
    us=set(user_ings)
    if us&SEAFOOD and recipe["_sf"]:
        for sf in SEAFOOD:
            if sf in rc: us=us|{sf}
    matched={u for u in us if u in rc or any(len(u)>2 and(u in r or r in u) for r in rc)}
    missing=sorted(rc-us)[:6]; overlap=len(matched)/max(len(rc),1)
    nb=min(0.30,sum(0.15 for u in us if u in norm(recipe["name"]))); mb2=min(0.20,(len(matched)-1)*0.06) if len(matched)>1 else 0
    tb=sum(0.04 for t in tags if t in q)+(0.05 if recipe.get("cuisine") and norm(recipe["cuisine"]) in q else 0)
    sp=0.35 if user_ings and user_ings[0] not in matched and not any(len(user_ings[0])>2 and(user_ings[0] in r or r in user_ings[0]) for r in rc) and not(user_ings[0] in SEAFOOD and recipe["_sf"]) else 0
    return min(1.0,overlap*0.70+nb*0.20+mb2+tb+ssc.get(recipe["id"],0)*0.10+mb)-sp,sorted(matched),missing

def do_search(query,user_ings,nlu,sess,top_k=10,meal_type=None,quick=False,diet_filter=None):
    excl=list(dict.fromkeys([canon(norm(e)) for e in nlu.get("exclude",[])+sess.get("exclude",[])]))
    ssc=ss(query); results=[]
    for r in R:
        sc,mat,mis=score_r(r,user_ings,excl,ssc,query,meal_type,quick,diet_filter)
        if sc<CUTOFF: continue
        results.append({"recipe":r,"score":sc,"missing":mis,"matched":mat,"match_pct":min(99,round(100*sc)) if user_ings else None})
    results.sort(key=lambda x:x["score"],reverse=True); return results[:top_k]

def find_sub(text,nlu):
    for i in nlu.get("ingredients",[]): c=canon(norm(i));
    if canon(norm(i)) in SUBS: return canon(norm(i))
    t=norm(text)
    for p in [r"substitute (?:for )?([a-z ]+?)(?:\?|$|,|\band\b)",r"replace (?:the )?([a-z ]+?)(?:\?|$|,)",r"instead of ([a-z ]+?)(?:\?|$|,)",r"without ([a-z ]+?)(?:\?|$|,)",r"alternative (?:to|for) ([a-z ]+?)(?:\?|$)"]:
        m=re.search(p,t)
        if m:
            c=canon(m.group(1).strip())
            if c in SUBS: return c
    return next((k for k in sorted(SUBS,key=len,reverse=True) if k in t),None)

async def handle(text,sess):
    nlu=await groq_nlu(text,sess["history"]); intent=nlu.get("intent","find_recipe")
    if sess.get("pending_gen") and intent not in("decline_gen","override_preference","greeting","help","substitution"):
        t=norm(text)
        if re.search(r'^(yes|sure|ok|yeah|go|please|generate|create|make it|do it|yep|yup|absolutely)\b',t): intent="confirm_gen"
        elif re.search(r'^(no|nope|skip|cancel|never mind)\b',t): intent="decline_gen"
    if intent=="confirm_gen":
        pg=sess.get("pending_gen");sess["pending_gen"]=None
        if not pg: return {"type":"error","message":"Please tell me what to generate!","recipes":[],"sub":None}
        gen=await groq_gen(pg["query"],sess.get("exclude",[]),sess.get("diet",[]))
        if gen:
            card={"id":"llm_gen","name":gen.get("name","AI Recipe"),"cuisine":gen.get("cuisine","Fusion"),"diet":gen.get("diet",[]),"time":gen.get("time","30 min"),"servings":gen.get("servings",4),"tags":gen.get("tags",[])+["ai-generated"],"ingredients":gen.get("ingredients",{}),"steps":gen.get("steps",[]),"match_pct":None,"missing":[],"matched_ingredients":[],"_is_llm_generated":True}
            return {"type":"recipes","message":f"✨ **AI-Generated: {card['name']}**\n\nCreated just for you!","recipes":[card],"sub":None}
        return {"type":"error","message":"⚠️ Generation failed. Try: *'generate a pasta recipe'*","recipes":[],"sub":None}
    if intent=="decline_gen": sess["pending_gen"]=None; return {"type":"decline","message":"👍 No problem! Try different ingredients or **'reset preferences'**.","recipes":[],"sub":None}
    if intent=="override_preference":
        ings=nlu.get("ingredients",[])
        if "__reset__" in ings: sess["exclude"]=[]; sess["diet"]=[]; sess["pending_gen"]=None; return {"type":"pref","message":"✅ All preferences reset! What would you like to cook?","recipes":[],"sub":None}
        restored=[]
        for ing in ings:
            c=canon(norm(ing))
            if c in sess["exclude"]: sess["exclude"].remove(c); restored.append(c)
            elif ing in sess["exclude"]: sess["exclude"].remove(ing); restored.append(ing)
        return {"type":"pref","message":f"✅ Removed **{', '.join(restored)}** from exclusions." if restored else "✅ Updated.","recipes":[],"sub":None}
    for e in nlu.get("exclude",[]): c=canon(norm(e)); c and c not in sess["exclude"] and sess["exclude"].append(c)
    for d in nlu.get("diet",[]): d not in sess["diet"] and sess["diet"].append(d)
    if intent=="greeting": return {"type":"greeting","message":"👋 Hey! I'm your Recipe Assistant.\n\n• **'I have chicken, rice'** — find recipes\n• **'veg recipes'** / **'no beef'** — filters\n• **'include chicken'** / **'reset preferences'** — undo\n• **'substitute for paneer'** — alternatives\n• **'random recipe'** — surprise!\n• Upload a photo 📷","recipes":[],"sub":None}
    if intent=="help": return {"type":"help","message":"🍳 Ingredient search · Veg/Non-veg/Vegan strict filtering · Meal type (breakfast/dessert/soup) · AI recipe generation · Substitution guide · OCR photos","recipes":[],"sub":None}
    if intent=="thanks": return {"type":"thanks","message":"😊 Happy cooking!","recipes":[],"sub":None}
    if intent=="substitution":
        t=find_sub(text,nlu)
        if t: return {"type":"sub","message":f"🔄 Substitutes for **{t}**:","recipes":[],"sub":{"ingredient":t,"options":SUBS[t]}}
        return {"type":"sub","message":"Couldn't identify ingredient. Try: *'substitute for paneer'*","recipes":[],"sub":None}
    if intent=="set_preference" and not nlu.get("ingredients"):
        parts=([f"excluding **{', '.join(sess['exclude'])}**"] if sess["exclude"] else [])+([f"**{', '.join(sess['diet'])}** diet"] if sess["diet"] else [])
        return {"type":"pref","message":"✅ Preferences: "+(", ".join(parts) or "none")+". Say *'reset preferences'* to undo.","recipes":[],"sub":None}
    if intent=="random_recipe":
        t=norm(text); nlu_d=nlu.get("diet",[]); rd=None
        if "vegetarian" in nlu_d or re.search(r'\bveg(etarian)?\b',t): rd="vegetarian"
        elif "vegan" in nlu_d: rd="vegan"
        elif "non-veg" in nlu_d or re.search(r'\bnon[- ]?veg\b',t): rd="non-veg"
        excl_s=set(sess.get("exclude",[])); passes=lambda r:not any(e in r["_ci"] for e in excl_s) and (not rd or (rd=="vegetarian" and("vegetarian" in r.get("diet",[]) or "vegan" in r.get("diet",[]))) or (rd=="vegan" and "vegan" in r.get("diet",[])) or (rd=="non-veg" and "non-veg" in r.get("diet",[])))
        av=[r for r in R if passes(r)] or [r for r in R if not rd or(rd=="vegetarian" and("vegetarian" in r.get("diet",[]) or "vegan" in r.get("diet",[]))) or(rd=="vegan" and "vegan" in r.get("diet",[])) or(rd=="non-veg" and "non-veg" in r.get("diet",[]))]
        picks=random.sample(av or R,min(5,len(av or R))); dl=f" **{rd}**" if rd else ""
        return {"type":"recipes","message":f"🎲 Here are **{len(picks)} random{dl} recipes**!","recipes":[{"id":r["id"],"name":r["name"],"cuisine":r["cuisine"],"diet":r["diet"],"time":r["time"],"servings":r["servings"],"tags":r.get("tags",[]),"ingredients":r.get("ingredients",{}),"steps":r.get("steps",[]),"match_pct":None,"missing":[],"matched_ingredients":[]} for r in picks],"sub":None}
    nlu_ings=[canon(norm(i)) for i in (nlu.get("ingredients") or [])]; rule_ings=extract_ings(text)
    user_ings=list(dict.fromkeys(nlu_ings+[i for i in rule_ings if i not in nlu_ings]))
    meal_type=nlu.get("meal_type") or detect_meal(text); quick=any(k in norm(text) for k in QUICK_KW); sq=nlu.get("query_for_search") or text
    dd,de=detect_diet(norm(text)); all_d=list(dict.fromkeys(dd+nlu.get("diet",[])+sess.get("diet",[])))
    df="vegan" if "vegan" in all_d else "vegetarian" if "vegetarian" in all_d else "non-veg" if "non-veg" in all_d else "pescatarian" if "pescatarian" in all_d else None
    sess["_adf"]=[df] if df else []; mn=dict(nlu); mn["exclude"]=list(dict.fromkeys(nlu.get("exclude",[])+de))
    hits=do_search(sq,user_ings,mn,sess,top_k=10,meal_type=meal_type,quick=quick,diet_filter=df)
    if not hits:
        sess["pending_gen"]={"query":text,"ingredients":user_ings}; excl_str=f" excluding **{', '.join(sess['exclude'])}**" if sess.get("exclude") else ""; mh=f" for **{meal_type}**" if meal_type else ""; dh=f" (**{df}**)" if df else ""
        return {"type":"no_result","message":f"😔 No matching recipes found{dh}{mh}{excl_str}.\n\n✨ **Want me to generate a custom AI recipe?** Say **yes**!","recipes":[],"sub":None}
    hits=await groq_rerank(user_ings,sq,hits,sess)
    excl_s=set(sess.get("exclude",[])+de)
    def pp(h):
        rc=h["recipe"]["_ci"]; rd=set(h["recipe"].get("diet",[]))
        if any(ex in rc or any(ex in r or r in ex for r in rc if len(ex)>3) for ex in excl_s): return False
        if df=="vegetarian" and "vegetarian" not in rd and "vegan" not in rd: return False
        if df=="vegan" and "vegan" not in rd: return False
        if df=="non-veg" and "non-veg" not in rd: return False
        return True
    filtered=[h for h in hits if pp(h)]; hits=filtered if filtered else hits; final=hits[:5]; top=final[0]
    exp=await groq_explain(top["recipe"],user_ings,top.get("matched",[])); ing_str=f" using **{', '.join(user_ings[:4])}**" if user_ings else ""; pct=f" ({top['match_pct']}% match)" if top["match_pct"] else ""
    msg=f"🍽️ Found **{len(final)} recipe{'s' if len(final)>1 else ''}**{ing_str}{pct}!\n\n💡 {exp}"
    if top["missing"]: msg+=f"\n\n⚠️ Top recipe also needs: **{', '.join(top['missing'][:4])}**"
    if sess.get("exclude"): msg+=f"\n✅ Excluded: **{', '.join(sess['exclude'])}**"
    if df: msg+=f"\n🥗 Filter: **{df}** only"
    return {"type":"recipes","message":msg,"recipes":[{"id":h["recipe"]["id"],"name":h["recipe"]["name"],"cuisine":h["recipe"]["cuisine"],"diet":h["recipe"]["diet"],"time":h["recipe"]["time"],"servings":h["recipe"]["servings"],"tags":h["recipe"].get("tags",[]),"ingredients":h["recipe"].get("ingredients",{}),"steps":h["recipe"].get("steps",[]),"match_pct":h["match_pct"],"missing":h["missing"],"matched_ingredients":h.get("matched",[])} for h in final],"sub":None}

def _ocr(img_bytes):
    try:
        import easyocr,numpy as np; from PIL import Image,ImageEnhance
        img=Image.open(io.BytesIO(img_bytes)).convert("RGB"); img=ImageEnhance.Contrast(ImageEnhance.Sharpness(img).enhance(2.0)).enhance(1.5)
        r=easyocr.Reader(["en"],gpu=False,verbose=False); txt=" ".join(r.readtext(np.array(img),detail=0,paragraph=True)); ings=extract_ings(txt)
        if ings: return ings
    except Exception as e: log.warning(f"EasyOCR:{e}")
    try:
        from PIL import Image,ImageFilter,ImageEnhance; import pytesseract
        img=Image.open(io.BytesIO(img_bytes)).convert("L"); img=ImageEnhance.Contrast(img.resize((img.width*2,img.height*2),Image.LANCZOS).filter(ImageFilter.SHARPEN)).enhance(2.5)
        return extract_ings(pytesseract.image_to_string(img,config="--psm 6 --oem 3"))
    except Exception as e: log.warning(f"Pytesseract:{e}"); return []

class ChatReq(BaseModel):
    session_id:str=""; message:str

@app.on_event("startup")
async def startup(): asyncio.create_task(asyncio.to_thread(get_chroma))

@app.post("/chat")
async def chat(req:ChatReq):
    sid=req.session_id or str(uuid.uuid4()); sess=get_sess(sid)
    sess["history"].append({"role":"user","content":req.message}); result=await handle(req.message,sess)
    sess["history"].append({"role":"assistant","content":result["message"]}); return {**result,"session_id":sid,"preferences":{"exclude":sess["exclude"],"diet":sess["diet"]}}

@app.post("/ocr")
async def ocr(file:UploadFile=File(...),session_id:str=Form(default="default")):
    detected=await asyncio.to_thread(_ocr,await file.read())
    if not detected: return {"session_id":session_id,"detected":[],"message":"⚠️ No ingredients detected. Try a clearer photo or type them.","recipes":[]}
    sess=get_sess(session_id); result=await handle("recipes with "+" ".join(detected),sess)
    return {"session_id":session_id,"detected":detected,"message":f"📸 Detected: **{', '.join(detected)}**\n\n"+result["message"],"recipes":result["recipes"]}

@app.post("/reset")
async def reset(body:dict):
    sid=body.get("session_id","")
    if sid in SESSIONS: del SESSIONS[sid]
    return {"status":"reset"}

@app.get("/health")
def health(): return {"status":"ok","recipes":len(R),"chroma":"ready" if _col else "loading","groq":"configured"}

@app.get("/")
def home(): return {"status":"online","version":"v6","recipes":len(R)}

if __name__=="__main__":
    import sys
    uvicorn.run("backend:app",host="0.0.0.0",port=8000,reload=False,log_level="info")
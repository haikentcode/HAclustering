from django.shortcuts import render,HttpResponse,render_to_response,HttpResponseRedirect
from django.contrib import auth
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans ,MiniBatchKMeans
from sklearn.metrics import adjusted_rand_score
import math
def kmensAlgo(documents,k=20):
         print "document Size",len(documents)
         vectorizer = TfidfVectorizer(stop_words='english')
         X = vectorizer.fit_transform(documents)
         true_k = k
         model = MiniBatchKMeans(n_clusters=true_k, init='k-means++', max_iter=200, n_init=1)
         model.fit(X)
         return model.predict(X)

def cdb(dbname):
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client[dbname]
    return db



def getProducts(cid=377,n=10**3):
    db = cdb("spmaster")
    c = db["product"]
    products = c.find({"category_id":cid}).limit(n)
    return products


def extractFeature(product):
       "return Feature list(tupple(feature_name,feature_value))"
       pf = product.get("product_features")
       feature = lambda x : { data["description"].lower():data["variant"] for data in x.values()}
       return feature(pf)



def featureClustring(request):
         cid = 377
         if request.POST:
               cid =int(request.POST.get("cid",377))

         products = getProducts(cid)
         totalProducts = 0

         features =[]
         for product in products :
               totalProducts +=1
               features.append(extractFeature(product))
         return render(request,"home/feature.html",{"features":features,"totalProducts":totalProducts})




def brandsClustring(request):
         cid = 377
         if request.POST:
               cid =int(request.POST.get("cid",377))
         
         noOfProducts = 10**4
         products = getProducts(cid)
         totalProducts = 0
         withbrands =[]
         withoudBrands=[]     

         for product in products :
               totalProducts +=1
               brand = extractFeature(product).get("brand",None)
               if brand:
                   withbrands.append((product["product"],brand))
               else:
                    withoudBrands.append(product["product"])
         k = len(withbrands)/ int(math.log(int(math.log(noOfProducts,2)),2))
         if request.POST:
           if int(request.POST.get("k",0)) > 1 and int(request.POST.get("k",0)) < totalProducts:
                k = int(request.POST.get("k",k))
         
         clusters={}
         print withbrands
         if totalProducts > 1 :
             a = kmensAlgo(map(lambda x:x[1],withbrands),k)
             print a
             for i,x in enumerate(a):
                 if clusters.get(x,None):
                     clusters[x].append(withbrands[i][1]+"-----------"+withbrands[i][0])
                 else:
                      clusters[x]=[withbrands[i][1]+"----------------"+withbrands[i][0]]
                         

         return render(request,"home/brands.html",{"clusters":clusters,"withbrands":withbrands,"withoudBrands":withoudBrands,"totalWithbrands":len(withbrands),"totalProducts":totalProducts,"k":k,"cid":cid})

            
def index(request):
     cid = 377
     if request.POST:
           cid =int(request.POST.get("cid",377))

     noOfProducts = 4*5*10**3
     products = getProducts(cid,noOfProducts)

     productsTitle = map(lambda x:x["product"],products)
     products = getProducts(cid,noOfProducts)
     productsinfo = map(lambda x:" |pid:"+str(x["product_id"])+" |mid:"+str(x["company_id"]),products)

     k = len(productsTitle)/ int(math.log(int(math.log(noOfProducts,2)),2))
     totalProducts = len(productsTitle)

     if request.POST:
           if int(request.POST.get("k",0)) > 1 and int(request.POST.get("k",0)) < totalProducts:
                k = int(request.POST.get("k",k))
     print "total item =%d and k=%d" %(totalProducts,k)
     clusters={}
     if totalProducts > 1 :
         a = kmensAlgo(productsTitle,k)
         for i,x in enumerate(a):
             if clusters.get(x,None):
                 clusters[x].append(productsTitle[i]+productsinfo[i])
             else:
                 clusters[x]=[productsTitle[i]+productsinfo[i]]
     return render(request,"home/home.html",{"clusters":clusters,"totalProducts":totalProducts,"k":k,"cid":cid})

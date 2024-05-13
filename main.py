import base64
import json
import os
import re
import string
import urllib.request
from string import digits

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ModelRecipe import ModelRecipe
from SQLquery import SQLWrapper

debug = False
folderRecipes = "./giallo_zafferano/Recipes"


def toDict(e):
    dizionario_spesa = {}
    for elemento in e:
        ingrediente     = elemento[0].replace("'", "''").replace(" ", "_")
        print(ingrediente)
        quantita        = elemento[1].replace("'", "''").replace(" ", "_")
        dizionario_spesa[ingrediente] = quantita

    json_spesa = json.dumps(dizionario_spesa, ensure_ascii=False)
    return json_spesa


def saveRecipe(linkRecipeToDownload, oldSoup):
    soup = downloadPage(linkRecipeToDownload)
    title = findTitle(soup)
    rating = findRating(oldSoup, title)

    if float(rating) > 5:
        rating = "3.3"
        

    filePath = calculateFilePath(title)
    if os.path.exists(filePath):
        return

    ingredients = findIngredients(soup)
    description = findDescription(soup)
    category = findCategory(soup)
    imageBase64, imageURL = findImage(soup)

    modelRecipe = ModelRecipe()
    modelRecipe.title = title
    modelRecipe.ingredients = ingredients
    modelRecipe.description = description
    modelRecipe.category = category
    modelRecipe.imageBase64 = imageBase64
    modelRecipe.linkToRecipe = linkRecipeToDownload
    modelRecipe.imageURL = imageURL
    modelRecipe.rating = rating

    dbConnection = SQLWrapper()
    dbConnection.createConnection()
    dbConnection.setQueryType("insert")
    
    for k, v in modelRecipe.toDictionary().items():
        if k == "ingredients":
            v = toDict(v)
        elif k == "description":
            # Esegui l'escape degli apostrofi nella descrizione per php
            v = v.replace("'", "''")
        print(f"add {k}")
        dbConnection.addValue(k, "" if type(v) == "NoneType" else v)
    
    dbConnection.sendRequest("POST", "/ricette.php/insert/ricette_rating")
    dbConnection.closeConnection()
    # createFileJson(modelRecipe.toDictionary(), filePath)

def findRating(oldSoup : BeautifulSoup, title):
    for ul_tag in oldSoup.find_all("ul", class_="gz-card-data top"):
        li_tags = ul_tag.find_all("li", class_="gz-single-data-recipe")
        matching_li_tags = [li for li in li_tags if li.find("a") and li.find("a").get("title") == title]
        if matching_li_tags:
            matching_li_tag = matching_li_tags[1] # prendo il secondo della lista
            rating_text = matching_li_tag.find("a").text.strip()
            return "3" if type(rating_text) == "NoneType" else rating_text.replace(",", ".")
    return "3"

def findTitle(soup):
    titleRecipe = ""
    for title in soup.find_all(attrs={"class": "gz-title-recipe gz-mBottom2x"}):
        titleRecipe = title.text
    return titleRecipe


def findIngredients(soup):
    allIngredients = []
    for tag in soup.find_all(attrs={"class": "gz-ingredient"}):
        link = tag.a.get("href")
        nameIngredient = tag.a.string
        contents = tag.span.contents[0]
        quantityProduct = re.sub(r"\s+", " ", contents).strip()
        allIngredients.append([nameIngredient.lower(), quantityProduct])
    return allIngredients


def findDescription(soup):
    allDescription = ""
    for tag in soup.find_all(attrs={"class": "gz-content-recipe-step"}):
        removeNumbers = str.maketrans("", "", digits)
        if hasattr(tag.p, "text"):
            description = tag.p.text.translate(removeNumbers)
            allDescription = allDescription + description
    return allDescription


def findCategory(soup):
    for tag in soup.find_all(attrs={"class": "gz-breadcrumb"}):
        try:
            category = tag.li.a.string
            return category
        except AttributeError:
            return ""


def findImage(soup):

    pictures = soup.find("picture", attrs={"class": "gz-featured-image"})

    if pictures is None:
        pictures = soup.find(
            "div", attrs={"class": "gz-featured-image-video gz-type-photo"}
        )

    imageSource = pictures.find("img")
    imageURL = imageSource.get("data-src")

    if imageURL is None:
        imageURL = imageSource.get("src")

    imageToBase64 = str(base64.b64encode(requests.get(imageURL).content))
    imageToBase64 = imageToBase64[2 : len(imageToBase64) - 1]
    return imageToBase64, imageURL


def calculateFilePath(title):
    compact_name = title.replace(" ", "_").lower()
    return folderRecipes + "/" + compact_name + ".json"


def createFileJson(data, path):
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False))


def downloadPage(linkToDownload):
    response = requests.get(linkToDownload)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def downloadAllRecipesFromGialloZafferano():
    totalPages = countTotalPages() + 1
    for pageNumber in tqdm(range(1, totalPages), desc="pages…", ascii=False, ncols=75):
        linkList = "https://www.giallozafferano.it/ricette-cat/page" + str(pageNumber)
        # linkList = "https://www.giallozafferano.com/latest-recipes/page" + str(pageNumber)
        response = requests.get(linkList)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(attrs={"class": "gz-title"}):
            link = tag.a.get("href")
            saveRecipe(link, soup)
            if debug:
                break

        if debug:
            break


def countTotalPages():
    numberOfPages = 0
    linkList = "https://www.giallozafferano.it/ricette-cat"
    # linkList = "https://www.giallozafferano.com/latest-recipes/"
    response = requests.get(linkList)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup.find_all(attrs={"class": "disabled total-pages"}):
        numberOfPages = int(tag.text)
    return numberOfPages


if __name__ == "__main__":
    if not os.path.exists(folderRecipes):
        os.makedirs(folderRecipes)
    downloadAllRecipesFromGialloZafferano()
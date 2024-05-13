class ModelRecipe:
    imageBase64 = ""
    title = ""
    category = ""
    description = ""
    linkToRecipe = ""
    imageURL = ""
    rating = ""
    ingredients = []

    def toDictionary(self):
        recipe = {
            "imageBase64": self.imageBase64,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "linkToRecipe" : self.linkToRecipe,
            "imageURL" : self.imageURL,
            "rating" : self.rating,
            "ingredients": self.ingredients,
        }
        return recipe

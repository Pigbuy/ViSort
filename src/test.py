from Errors import ErrorMan

with ErrorMan.branch("baking cookies"):
    print("baking cookies is fun")
    with ErrorMan.branch("making dough"):
        print("making dough is fun")
        ErrorMan.queue_error("FAILED TO MAKE THE DOUGH", "I DONT HAVE ALL INGREDIENTS")
    with ErrorMan.branch("baking the dough in the oven"):
        print("YAAY I LOVE BAKING THE DOUGH IN THE OVEN")
        ErrorMan.queue_error("COULDNT TURN ON THE OVEN", "THE OVEN BROKE")
        with ErrorMan.branch("putting cookie dough inside the oven"):
            ErrorMan.queue_error("COULDNT PUT COOKIE DOUGH IN THE OVEN","I HAVEN MADE THE COOKIE DOUGH")

with ErrorMan.branch("eating the cookies"):
    ErrorMan.queue_error("COULDNT EAT THE COOKIES","COOKIES WERENT MADE :(")

ErrorMan.throw_if_errors()
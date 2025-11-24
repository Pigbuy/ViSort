from Errors import Errors

with Errors.branch("baking cookies"):
    print("baking cookies is fun")
    with Errors.branch("making dough"):
        print("making dough is fun")
        Errors.queue_error("FAILED TO MAKE THE DOUGH", "I DONT HAVE ALL INGREDIENTS")
    with Errors.branch("baking the dough in the oven"):
        print("YAAY I LOVE BAKING THE DOUGH IN THE OVEN")
        Errors.queue_error("COULDNT TURN ON THE OVEN", "THE OVEN BROKE")
        with Errors.branch("putting cookie dough inside the oven"):
            Errors.queue_error("COULDNT PUT COOKIE DOUGH IN THE OVEN","I HAVEN MADE THE COOKIE DOUGH")

with Errors.branch("eating the cookies"):
    Errors.queue_error("COULDNT EAT THE COOKIES","COOKIES WERENT MADE :(")

Errors.throw_if_errors()
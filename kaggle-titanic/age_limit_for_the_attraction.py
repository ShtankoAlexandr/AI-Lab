# Как волонтер на фестивале, ты отслеживаешь установку аттракционов.
# У нас есть класс с именем Ride, который хранит название аттракциона и
# подходящую возрастную группу. Используй экземпляры этого класса, чтобы
# отслеживать аттракционы, установленные сегодня.

# Создай новый экземпляр класса Ride с именем roller_coaster и укажи, что его
# название Roller coaster и это аттракцион для adults.
# Создай новый экземпляр класса Ride с именем ferris_wheel и укажи, что его
# название Ferris wheel и это аттракцион для kids.


class Ride:
    def __init__(self, name, age_group):
        self.name = name
        self.age_group = age_group


roller_coaster = Ride("Roller coaster", "adults" )
ferris_wheel = Ride("Ferris wheel", "kids")

print(roller_coaster.age_group)
print(ferris_wheel.name)

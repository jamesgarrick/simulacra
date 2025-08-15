from typing import List
import ollama
import time

# 1 = grass

class World:
    def __init__(self):
        pass

    world = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    # N = same col, +1 row
    # S = same col, -1 row
    # E = same row, +1 col
    # W = same row, -1 col

    # 2, 3

    worldSize = [len(world[0]), len(world)]
    # y = num rows = len
    # x = num cols  len(len)
    # x, y




class Person:
    def __init__(self, name, age, position, world, description):
        self.name: str = name
        self.age: int = age
        self.position: List[float] = position
        self.world: World = world
        self.description = description

    def getPosition(self):
        return self.position

    def setPosition(self, position: List[float]):
        if len(position) != 2: # 2D coordinates
            print(f"ERROR: {position} is not a valid world coordinate.")
            return

        x = position[0]
        y = position[1]

        if x > self.world.worldSize[0] or y > self.world.worldSize[1]:
            print(f"ERROR: {position} is outside of world bounds.")
            return

        if x < 0 or y < 0:
            print(f"ERROR: {position} is not a valid world coordinate.")
            return

        # finally, set position
        self.position = position

    def getModelCard(self):
        return f"""
            You are {self.name}, aged {self.age}.
            {self.description}
            """

    def perceive(self):
        pass

    def act(self, action: str):
        action = action.replace("action =", "")
        print(f"New action {action}")
        print(action.split("("))
        if action.split("(")[0].replace(" ","") == "move":
            direction = action.split("(")[1].replace(")","")
            print(direction)
            position = self.getPosition()
            print(f"Position: {position}")
            if direction == "north":
                self.setPosition([position[0], position[1] + 1])
            elif direction == "south":
                self.setPosition([position[0], position[1] - 1])
            elif direction == "east":
                self.setPosition([position[0] + 1, position[1]])
            elif direction == "west":
                self.setPosition([position[0] - 1, position[1]])
    # nothing, say(message)
    actions = ["move(north/east/south/west"]


def main():
    print("Simulacra Research Project")

    print("Loading world...")
    world = World()
    print("World loaded...")

    print("Creating base population...")
    test_person_1 = Person("Jeff", 27, [1,3], world, "Tacky yet mindful man that enjoys playing golf and understanding the world.")

    population = [test_person_1]
    print("Base population created...")

    print("Simulation running...")

    simulacra_iteration = 1
    while True:
        print(f"Iteration {simulacra_iteration}")
        for person in population:
            print("--ITER--")
            print(person.getPosition())
            response: str = (ollama.generate(model='llama3', prompt=(person.getModelCard() + f"You have the following options available to you: {person.actions}. As {person.name}, please respond with and only with an action and supported arguments, AND NOTHING ELSE. For example: move(east)"))['response'])
            print(response)
            if response.find("move") != -1:
                person.act(response)
            elif response.find("nothing") != -1:
                pass
        time.sleep(1)
        simulacra_iteration += 1

if __name__ == "__main__":
    main()

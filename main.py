from typing import List
import pygame
import ollama
import time

# 1 = grass

TILE_SIZE = 200
GRASS_COLOR = (34, 139, 34)
CHAR_COLOR = (255, 0, 0)
GUI_ENABLED = True
ITERATIONS_PER_DAY = 50  # after which triggers EOD reflection, and then reset

tiles = {1: "grass", 2: "stone"}


def tileIDToName(tileId: int) -> str:
    return tiles.get(tileId, default=-1)


def draw_world(screen, world, population) -> None:
    for y, row in enumerate(world.world):  # y = row
        for x, tile in enumerate(row):  # x = col
            px, py = x * TILE_SIZE, y * TILE_SIZE
            pygame.draw.rect(screen, GRASS_COLOR, (px, py, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (0, 0, 0), (px, py, TILE_SIZE, TILE_SIZE), 1)

    # Draw each person in population
    for person in population:
        x, y = person.getPosition()
        pygame.draw.circle(
            screen,
            CHAR_COLOR,
            (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2),
            TILE_SIZE // 3,
        )


class World:
    def __init__(self):
        self.world = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2],
            [1, 2, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 2, 1],
        ]

        self.worldSize = [len(self.world[0]), len(self.world)]

    def getTileID(self, x: int, y: int) -> int:
        """Gets tile ID. **-1 if tile doesn't exist**"""
        try:
            return self.world[y][x]
        except IndexError:
            return -1


class Person:
    def __init__(self, name, age, position, world, description, memoryStream=[]):
        self.name: str = name
        self.age: int = age
        self.position: List[float] = position
        self.world: World = world
        self.description: str = description
        self.memoryStream: List[str] = memoryStream

    def addMemory(self, memory: str) -> None:
        self.memoryStream.append(memory)

    def getMemories(self, count: str = -1) -> List[str]:
        if count == -1:
            return self.memoryStream
        else:
            return self.memoryStream[-count:]

    def getPosition(self) -> List[float]:
        return self.position

    def setPosition(self, position: List[float]) -> None:
        if len(position) != 2:  # 2D coordinates
            print(f"ERROR: {position} is not a valid world coordinate.")
            return

        x = position[0]
        y = position[1]

        if x >= self.world.worldSize[0] or y >= self.world.worldSize[1]:
            print(f"ERROR: {position} is outside of world bounds.")
            return

        if x < 0 or y < 0:
            print(f"ERROR: {position} is not a valid world coordinate.")
            return

        # finally, set position
        self.position = position

    def canMove(self, position: List[float]) -> bool:
        if len(position) != 2:  # 2D coordinates
            return False

        x = position[0]
        y = position[1]

        if x >= self.world.worldSize[0] or y >= self.world.worldSize[1]:
            return False

        if x < 0 or y < 0:
            return False

        return True

    def getModelCard(self) -> str:
        return f"""
            You are {self.name}, aged {self.age}.
            {self.description}
            """

    def perceive(self):
        pass

    def act(self, action: str) -> None:
        action = action.replace("action =", "")
        print(f"New action {action}")
        print(action.split("("))
        if action.split("(")[0].replace(" ", "") == "move":
            direction = action.split("(")[1].replace(")", "")
            print(direction)
            x, y = self.getPosition()

            if direction == "north":
                self.setPosition([x, y - 1])
                self.addMemory("You moved north")
            elif direction == "south":
                self.setPosition([x, y + 1])
                self.addMemory("You moved south")
            elif direction == "east":
                self.setPosition([x + 1, y])
                self.addMemory("You moved east")
            elif direction == "west":
                self.setPosition([x - 1, y])
                self.addMemory("You moved west")

    # nothing, say(message)
    def getAllowedMoves(self) -> List[str]:
        moves = []
        x, y = self.getPosition()
        if self.canMove([x, y - 1]):
            moves.append("north")
        if self.canMove([x, y + 1]):
            moves.append("south")
        if self.canMove([x + 1, y]):
            moves.append("east")
        if self.canMove([x - 1, y]):
            moves.append("west")

        return moves

    def getActions(self) -> str:
        directions = self.getAllowedMoves()
        return [f"move({'/'.join(directions)})"]


def main():
    print("Simulacra Research Project")

    print("Loading world...")
    if GUI_ENABLED:
        pygame.init()
        print("GUI Enabled, PyGame loaded...")

    world = World()
    print("World loaded...")
    if GUI_ENABLED:
        screen = pygame.display.set_mode(
            (len(world.world[0]) * TILE_SIZE, len(world.world) * TILE_SIZE)
        )
        clock = pygame.time.Clock()

    print("Creating base population...")
    test_person_1 = Person(
        "Jeff",
        27,
        [1, 2],
        world,
        "Tacky yet mindful man that enjoys playing golf and understanding the world.",
    )

    population = [test_person_1]
    print("Base population created...")

    print("Simulation running...")
    running = True

    simulacra_iteration = 1
    while running:
        print(f"Iteration {simulacra_iteration}")
        for person in population:
            print(person.getPosition())
            print(f"Actions available: {person.getActions()}")
            response: str = ollama.generate(
                model="gpt-oss",
                prompt=(
                    person.getModelCard()
                    + "Your memories: "
                    + ", ".join(person.getMemories(5))
                    + "."
                    + f"You have the following options available to you: {person.getActions()}. As {person.name}, please respond with and only with an action and supported arguments, AND NOTHING ELSE. For example: move(east)"
                ),
            )["response"]
            print(response)
            if response.find("move") != -1:
                person.act(response)
            elif response.find("nothing") != -1:
                pass
        time.sleep(1)
        simulacra_iteration += 1

        if GUI_ENABLED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))
            draw_world(screen, world, population)
            pygame.display.flip()
            clock.tick(10)


if __name__ == "__main__":
    main()

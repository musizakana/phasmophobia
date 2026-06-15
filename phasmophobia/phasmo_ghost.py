import random
from collections import Counter

class Game():
    def __init__(self, average_san=100, is_solo=True, activity_level="low", is_bloodmoon=False, roam_frequency="High"):
        self.average_san = average_san
        self.is_solo = is_solo
        self.activity_level = activity_level
        self.is_bloodmoon = is_bloodmoon
        self.roam_frequency = roam_frequency
        self.erapsed_time = 0
        return
    

class Ghost():
    def __init__(self, game):
        self.game = game
        self._awake = False
        self._favorite_room = None
        self._type = None
        self._types = {"Aswang", "Banshee", "Dayan", "Demon", "Deogen", "Gallu", "Goryo", 
                        "Hantu", "Jinn", "Kormos", "Mare", "Moroi", "Myling", "Obake", "Obambo",
                        "Oni", "Onryo", "Phantom", "Poltergeist", "Raiju", "Revenant", "Shade",
                        "Spirit", "Thaye", "The Mimic", "The Twins", "Wraith", "Yokai", "Yurei"}
        self._incense_activity = 0.0
        self._obambo_state = "calm"
        self._thaye_agecount = 0
        self.stats = Counter()
        
    
    def set_type(self, type):
        if type not in self._types: raise ValueError()
        self._type = type
        return
    
    def wakeup(self):
        if self._type is None:
            print('Ghost type is None. Please try Ghost.set_type()')
            return
        self._incense_activity = 0.0
        self._obambo_state = "calm"
        self._thaye_agecount = 0
        self.stats = Counter()
        self.game.erapsed_time = 0
        self._awake = True
        return
    
    def sleep(self):
        self._awake = False
        return

    def is_awake(self):
        return self._awake

    def main_loop(self):
        if not self.is_awake():
            print('Ghost is NOT awake. Please try Ghost.wakeup()')
            return
        erapsed_minute = self.game.erapsed_time // 60
        self._obambo_state = "calm" if erapsed_minute % 4 == 1 or erapsed_minute % 4 == 2 else "aggressive"
        self.activity()
        self.idle()
        return

    def activity(self, oni_activity=False, yokai_activity=False):
        self.stats['activity'] += 1
        activity_value = 0
        activity_value += int(100 - self.game.average_san)
        activity_value += 15 if self.game.is_solo else 0
        activity_value += int(self._incense_activity)
        activity_value += 30 if oni_activity else 0
        activity_value += 30 if yokai_activity else 0
        activity_value *= (2 - 1.5 * self._thaye_agecount / 10) if self._type == "Thaye" else 1
        if self._type == "Obambo":
            activity_value = (
                90 if self._obambo_state == "calm" else
                25 if self._obambo_state == "aggressive" else
                activity_value)
        activity_value = min(activity_value, 100)
        activity_threshold = {
            "high": 100,
            "medium": 115,
            "low": 130
        }.get(self.game.activity_level, 130)
        activity_threshold -= 15 if self.game.is_bloodmoon else 0
        if self._type == "Shade":
            activity_threshold = int(activity_threshold * 1.5)
        if random.randint(1, 100) <= 50 and activity_value <= random.randint(0, activity_threshold - 1):
            # success
            # random.choices()はリストを返すので[0]で中身を取る
            # weightsで指定すると相対重みで指定する、累積重みで指定したいならcum_weightsに渡す
            random.choices(
                [self.roaming, self.ability, self.interaction],
                weights=[2, 4, 5],
                k=1
            )[0]()
        else:
            # failed
            def room_event():
                random.choices(
                    [self.interaction, self.favorite_room],
                    weights=[1, 3],
                    k=1,
                )[0]()
                return
            # weights = [roaming_weight, room_event_weight]
            weights = [1, 5] if self._type == "Goryo" else [1, 2]
            random.choices(
                [self.roaming, room_event],
                weights=weights,
                k=1,
            )[0]()
        return

    def roaming(self, is_lightroom=False):
        dots_threshold = 2 if self._type == "Goryo" else 1
        if random.randint(1, 3) <= dots_threshold:
            self.dots()
            return
        def short_roaming():
            pass
        def long_roaming():
            pass
        # バンシー、メアー、御霊の分岐
        if self._type == 'Goryo':
            weights = [1, 0]
        elif self._type == 'Banshee':
            weights = [5, 5]
        elif self._type == 'Mare' and is_lightroom:
            weights = [5, 5]
        else:
            weights = {
                "high": [7, 3],
                "medium": [8, 2],
                "low": [9, 1]
            }.get(self.game.roam_frequency, [7, 3])
        random.choices(
            [short_roaming, long_roaming],
            weights=weights
        )[0]()
        return

    def dots(self):
        self.stats["dots"] += 1
        return

    def ability(self):
        pass

    def interaction(self):
        pass

    def favorite_room(self):
        if self._type == "Goryo" and random.randint(1, 10) == 1:
            self.dots()
            return
        return

    def idle(self):
        self.game.erapsed_time += random.randint(2, 6)
        return
    

def main():
    activate_counts = []
    dots_counts = []
    N = 200
    for _ in range(N):
        game = Game()
        ghost = Ghost(game)
        ghost.set_type('Aswang')
        ghost.wakeup()
        while game.erapsed_time <= 1800:
            ghost.main_loop()
        activate_counts.append(ghost.stats['activity'])
        dots_counts.append(ghost.stats['dots'])
    import pandas as pd
    activity_df = pd.DataFrame(activate_counts)
    dots_df = pd.DataFrame(dots_counts)
    print("activity:")
    print(activity_df.describe())
    print("D.O.T.S:")
    print(dots_df.describe())

if __name__ == "__main__":
    main()
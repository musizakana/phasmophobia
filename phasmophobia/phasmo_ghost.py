import random
from collections import Counter

class Game():
    def __init__(self, average_san=100, is_solo=True, activity_level="low", is_bloodmoon=False, \
                roam_frequency="high", event_frequency="high"):
        self.average_san = average_san
        self.is_solo = is_solo
        self.activity_level = activity_level
        self.is_bloodmoon = is_bloodmoon
        self.roam_frequency = roam_frequency
        self.event_frequency = event_frequency
        self.elapsed_time = 0
        return
    def san_decrease(self, san_diff):
        self.average_san = max(0, self.average_san - san_diff)
        return self.average_san

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
        self.game.elapsed_time = 0
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
        elapsed_minute = self.game.elapsed_time // 60
        self._obambo_state = "aggressive" if elapsed_minute % 4 == 1 or elapsed_minute % 4 == 2 else "calm"
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
        if random.randint(1, 100) <= 50 and activity_value >= random.randint(0, activity_threshold - 1):
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
            self.game.elapsed_time += random.randint(1, 3)
            return
        def long_roaming():
            self.game.elapsed_time += random.randint(3, 9)
            return
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
        self.game.elapsed_time += random.randint(1, 3)
        self.stats["dots"] += 1
        return

    def ability(self):
        self.stats['ability'] += 1
        def rand_gen():
            r = random.randint(0, 11) if self._type != "Thaye" else \
                int(random.uniform(0.0, 12.0)*(2 - 1.5 * self._thaye_agecount / 10))
            return r
        rand = rand_gen()
        # 難易度による超常現象リロール
        if self.game.event_frequency == "low" and rand >= 7:
            rand = rand_gen()
        elif self.game.event_frequency == "high" and rand <= 6:
            rand = rand_gen()
        # ブラッドムーンによるリロール、難易度とは別枠
        if self.game.is_bloodmoon and rand <= 6:
            rand = rand_gen()
        # アビリティ判定
        def fuse_box():
            self.stats['fuse_box'] += 1
            return
        def proper_ability():
            self.stats['proper_ability'] += 1
            # ソロの場合のみ
            if self._type == "Yurei":
                self.game.san_decrease(15)
            if self._type == "Jinn":
                self.game.san_decrease(25)
            return
        def ghost_event():
            # 正気度減少周りはソロのみ正しく計算できている
            self.stats['ghost_event'] += 1
            def singing():
                self.stats['singing'] += 1
                return
            def standing():
                self.stats['standing'] += 1
                return
            def light_breaking():
                self.stats['light_breaking'] += 1
                return
            def red_light():
                self.stats['red_light'] += 1
                return
            def chasing():
                self.stats['chasing'] += 1
                san_decrease = 10 if self._type != "Oni" else 20
                self.game.san_decrease(san_decrease)
                return
            def mist_form():
                self.stats['mist_form'] += 1
                self.game.san_decrease(10)
                return
            def appear():
                self.stats['appear'] += 1
                return
            # [singing, standing, light_breaking, red_light, chasing, mist_form, appear]
            standard = [3, 1, 1, 1, 3, 3, 3]
            weights = {
                'Banshee': [21, 2, 2, 2, 6, 6, 6],
                'Kormos': [3, 1, 1, 1, 0, 0, 3],
                'Mare': [9, 2, 5, 2, 9, 9, 9],
                'Oni': [3, 1, 1, 1, 6, 0, 3],
                'Shade': [0, 1, 1, 1, 3, 9, 0]
            }.get(self._type, standard)
            random.choices(
                [singing, standing, light_breaking, red_light, chasing, mist_form, appear],
                weights=weights
            )[0]()
            return
        if rand == 0:
            fuse_box()
        elif 1 <= rand and rand <= 4:
            proper_ability()
        elif rand == 5 and self._type == "Hantu":
            fuse_box()
        else:
            ghost_event()
        return

    def interaction(self):
        pass

    def favorite_room(self):
        self.game.elapsed_time += random.randint(1, 3)
        if self._type == "Goryo" and random.randint(1, 10) == 1:
            self.dots()
            return
        return

    def idle(self):
        self.game.elapsed_time += random.randint(2, 6)
        return
    

def main():
    activate_counts = []
    average_san_counts = []
    ability_counts = []
    ghost_event_counts = []
    N = 200
    for _ in range(N):
        game = Game(average_san=95,activity_level='low',event_frequency="high")
        ghost = Ghost(game)
        ghost.set_type('Jinn')
        ghost.wakeup()
        while game.elapsed_time <= 600:
            ghost.main_loop()
        activate_counts.append(ghost.stats['activity'])
        average_san_counts.append(ghost.game.average_san)
        ability_counts.append(ghost.stats['ability'])
        ghost_event_counts.append(ghost.stats['ghost_event'])
    import pandas as pd
    activity_df = pd.DataFrame(activate_counts)
    average_san_df = pd.DataFrame(average_san_counts)
    ability_df = pd.DataFrame(ability_counts)
    ghost_event_df = pd.DataFrame(ghost_event_counts)
    print("activity:")
    print(activity_df.describe())
    print('average san:')
    print(average_san_df.describe())
    print("ability:")
    print(ability_df.describe())
    print('ghost event:')
    print(ghost_event_df.describe())

if __name__ == "__main__":
    main()
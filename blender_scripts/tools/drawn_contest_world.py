import bpy
import imp
#from random import random, randrange, choice, gauss, uniform
#from copy import copy
import pickle

import bobject
imp.reload(bobject)
from bobject import Bobject

from hawk_dove import TRAIT_MODE

#from graph_bobject import GraphBobject

from blobject import Blobject

import helpers
imp.reload(helpers)
from helpers import *


BASE_CREATURE_SCALE = 0.04
CREATURE_HEIGHT_FACTOR = 0.8
#CREATURE_HOME_DISTANCE = 1.2

BASE_FOOD_SCALE = 0.05
FOOD_PATTERN_MULTIPLE = 6 #Geometry of food pattern
FOOD_PATTERN_ANGLE_OFFSET = 6
FOOD_EDGE_RATIO = 0.8

CREATURE_MOVE_DURATION = 0.5
PAUSE_LENGTH = 0#.25

'''
Improvements
- Cascade going out/in
- Make stationary point not a creature
- Add vines to food plants
'''

class DrawnCreature(Blobject):
    """docstring for DrawnCreature."""
    def __init__(
        self,
        creature = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.creature = creature
        if self.creature == None:
            raise Warning('DrawnCreature needs creature.')

        self.apply_material_by_fight_chance()

    def apply_material_by_fight_chance(self):
        color = mix_colors(
            COLORS_SCALED[2],
            COLORS_SCALED[5],
            self.creature.fight_chance
        )

        self.color_shift(
            duration_time = None,
            color = color,
            start_time = - 1 / FRAME_RATE,
            shift_time = 1 / FRAME_RATE,
            obj = self.ref_obj.children[0].children[0]
        )

class DrawnFood(Bobject):
    def __init__(self, object_model, **kwargs):
        super().__init__(
            objects = [object_model.copy()],
            name = 'food',
            **kwargs
        )

class DrawnWorld(Bobject):
    """docstring for DrawnWorld."""

    def __init__(
        self,
        sim = None,
        phase_durations = {
            'day_prep' : CREATURE_MOVE_DURATION,
            'creatures_go_out' : CREATURE_MOVE_DURATION,
            'pause_before_contest' : 0,
            'contest' : CREATURE_MOVE_DURATION,
            'pause_before_home' : PAUSE_LENGTH,
            'creatures_go_home' : CREATURE_MOVE_DURATION,
            'pause_before_reset' : 0,
            'food_disappear' : CREATURE_MOVE_DURATION,
        },
        scale = 5,
        creature_scale = None,
        name = 'world',
        loud = False,
        linked_graph = None,
        bounded_regions = True, #For testing
        wiggle = False,
        **kwargs
    ):
        super().__init__(scale = scale, name = name, **kwargs)

        if sim == None:
            raise Warning('DrawnWorld needs a market sim to draw')
        elif isinstance(sim, str):
            result = os.path.join(
                SIM_DIR,
                sim
            ) + ".pkl"
            if loud:
                print(result)
            with open(result, 'rb') as input:
                if loud:
                    print(input)
                self.sim = pickle.load(input)
            if loud:
                print("Loaded the world")
        else:
            self.sim = sim

        self.phase_durations = phase_durations

        #Initialize drawn_creature property of creature objects
        for day in self.sim.calendar:
            for cre in day.creatures:
                cre.drawn_creature = None
            for cre in day.next_creatures:
                cre.drawn_creature = None
                #Will be redundant in most cases, but catches last creatures

        self.drawn_creatures = []
        self.reusable_creatures = []
        self.reusable_food = []
        self.reusable_halves = []
        self.creature_scale = creature_scale
        if self.creature_scale == None:
            self.creature_scale = BASE_CREATURE_SCALE
            ##TODO: make this depend on food count.
        self.wiggle = wiggle

        self.elapsed_time = 0

        food_bobject_model = import_object(
            'goodicosphere', 'primitives',
        )
        self.food_object_model = food_bobject_model.ref_obj.children[0]

        #Another model for half food, since food splits
        half_food_bobject_model = import_object(
            'half_icosphere', 'primitives',
        )
        self.half_food_object_model = half_food_bobject_model.ref_obj.children[0]

        #half_food_bobject_model.add_to_blender(appear_time = 0)

        self.linked_graph = linked_graph
        if self.linked_graph != None:
            self.add_functions_to_graph(bounded_regions = bounded_regions)

    def add_to_blender(self, appear_time = None, **kwargs):
        if appear_time == None:
            raise Warning('Need appear_time for DrawnWorld.add_to_blender()')

        self.appear_time = appear_time

        floor = import_object(
            'disc', 'primitives',
            location = [0, 0, 0],
            name = 'ground'
        )
        apply_material(floor.ref_obj.children[0], 'color2')
        self.add_subbobject(floor)
        super().add_to_blender(appear_time = self.appear_time, **kwargs)

        '''self.draw_initial_creatures(
            start_time = self.appear_time + OBJECT_APPEARANCE_TIME / FRAME_RATE
        )'''

        '''self.set_food(
            start_time = self.appear_time + OBJECT_APPEARANCE_TIME / FRAME_RATE,
            day = self.sim.calendar[0]
        )'''

    def update_creatures(
        self,
        start_time = None,
        end_time = None,
        day = None,
        is_first_day = False,
        updating_next = False, #For showing results of last day
        graph_only = False
    ):
        if start_time == None:
            raise Warning('Need start_time for update_creatures')
        if end_time == None:
            end_time = start_time + OBJECT_APPEARANCE_TIME / FRAME_RATE

        if updating_next == False:
            creatures = day.creatures #self.sim.calendar[0].creatures
        elif updating_next == True:
            creatures = day.next_creatures
        angle_inc = 2 * math.pi / len(creatures)
        radius = 1 - self.creature_scale

        if graph_only == False:
            old_creatures = []
            #new creatures
            #doing these first to avoid updating positions of old creatures so new
            #creatures can appear to come from old ones.
            for i, cre in enumerate(creatures):
                angle = i * angle_inc

                if cre.drawn_creature != None:
                    old_creatures.append(cre)
                else:
                    destination = [
                        radius * math.cos(math.pi / 2 + angle),
                        radius * math.sin(math.pi / 2 + angle),
                        self.creature_scale * CREATURE_HEIGHT_FACTOR
                    ]

                    if is_first_day == True: #day.date == 0:
                        start_loc = destination
                    else:
                        start_loc = cre.parent.drawn_creature.ref_obj.location

                    reusables = [x for x in self.reusable_creatures if x.creature.fight_chance == cre.fight_chance]
                    if len(reusables) > 0:
                        d_cre = reusables[0]
                        self.reusable_creatures.remove(d_cre)
                        d_cre.creature = cre
                        d_cre.move_to(
                            new_location = start_loc,
                            new_angle = [math.pi / 2, 0, angle],
                            #scale = self.creature_scale,
                            end_time = start_time,
                            start_frame = start_time * FRAME_RATE - 1
                        )
                        d_cre.move_to(
                            new_scale = self.creature_scale,
                            start_time = start_time,
                            end_time = end_time
                        )

                    else:
                        d_cre = DrawnCreature(
                            creature = cre,
                            location = start_loc,
                            rotation_euler = [math.pi / 2, 0, angle],
                            scale = self.creature_scale,
                            wiggle = self.wiggle
                        )
                        self.add_subbobject(d_cre)
                        d_cre.add_to_blender(
                            appear_time = start_time,
                            transition_time = (end_time - start_time) * FRAME_RATE
                            #subbobject_timing = (end_time - start_time) * FRAME_RATE
                        )

                    self.drawn_creatures.append(d_cre)
                    cre.drawn_creature = d_cre

                    if is_first_day == False:
                        d_cre.move_to(
                            new_location = destination,
                            start_time = start_time,
                            end_time = end_time
                        )

            #old creatures
            for i, cre in enumerate(creatures):
                angle = i * angle_inc

                if cre in old_creatures:
                    destination = [
                        radius * math.cos(math.pi / 2 + angle),
                        radius * math.sin(math.pi / 2 + angle),
                        self.creature_scale * CREATURE_HEIGHT_FACTOR
                    ]
                    cre.drawn_creature.move_to(
                        new_location = destination,
                        start_time = start_time,
                        end_time = end_time
                    )

            #clean up dead creatures
            new_reusable_creatures = []
            for d_cre in self.drawn_creatures:
                alive = False
                for cre in creatures:
                    if cre.drawn_creature == d_cre:
                        alive = True
                        break
                if alive == False:
                    #d_cre.disappear(disappear_time = end_time)#start_time + OBJECT_APPEARANCE_TIME / FRAME_RATE)
                    d_cre.move_to(
                        new_scale = 0,
                        start_time = start_time,
                        end_time = end_time
                    )
                    new_reusable_creatures.append(d_cre)

            #print('New reusable creatures')
            for d_cre in new_reusable_creatures:
                #print(str(d_cre.name) + ' ' + str(d_cre.creature.fight_chance))
                self.drawn_creatures.remove(d_cre)
                self.reusable_creatures.append(d_cre)


        if self.linked_graph != None:
            if updating_next == False:
                self.update_graph(
                    date = day.date,
                    start_time = start_time,
                    end_time = end_time
                )
            elif updating_next == True:
                self.update_graph(
                    date = day.date + 1,
                    start_time = start_time,
                    end_time = end_time
                )

    def set_food(
        self,
        start_time = None,
        duration_time = None,
        end_time = None,
        day = None
    ):
        if start_time == None:
            raise Warning('Need start_time for set_food')
        if duration_time != None and end_time != None:
            raise Warning('Cannot set both duration_time and end_time in set_food')
        if duration_time == None and end_time == None:
            duration_time = OBJECT_APPEARANCE_TIME / FRAME_RATE
        if end_time != None:
            duration_time = end_time - start_time

        if day == None:
            raise Warning('Need day for set_food')

        pair_count = len(day.food_objects)
        ring_count = 0
        while pair_count > 0:
            if ring_count == 0:
                pair_count -= 1
            else:
                pair_count -= ring_count * FOOD_PATTERN_MULTIPLE

            ring_count += 1

        locations = helpers.circle_grid(
            num_rings = ring_count,
            dot_count_multiple = FOOD_PATTERN_MULTIPLE,
            rot_add = FOOD_PATTERN_ANGLE_OFFSET,
        )
        for i in range(len(locations)):
            locations[i] = scalar_mult_vec(locations[i], FOOD_EDGE_RATIO)

        delay = (duration_time - OBJECT_APPEARANCE_TIME / FRAME_RATE) / len(day.food_objects)
        for i, pair in enumerate(day.food_objects):
            f_scale = BASE_FOOD_SCALE / ring_count
            pair.location = locations[i]
            pair.angle = math.atan2(locations[i][1], locations[i][0])

            #reusables = [x for x in self.reusable_creatures if x.creature.fight_chance == cre.fight_chance]
            if len(self.reusable_food) > 1:
                food1 = self.reusable_food[0]
                self.reusable_food.remove(food1)
                food1.move_to(
                    new_location = [
                        locations[i][0] - 0.9 * f_scale * math.cos(pair.angle + math.pi / 2),
                        locations[i][1] - 0.9 * f_scale * math.sin(pair.angle + math.pi / 2),
                        f_scale,
                    ],
                    end_time = start_time,
                    start_frame = start_time * FRAME_RATE - 1
                )
                world_const = food1.ref_obj.constraints[0]
                world_const.keyframe_insert(
                    data_path = 'influence',
                    frame = start_time * FRAME_RATE - 1
                )
                world_const.influence = 1
                world_const.keyframe_insert(
                    data_path = 'influence',
                    frame = start_time * FRAME_RATE
                )

                food1.move_to(
                    new_scale = f_scale,
                    start_time = start_time + i * delay,
                    end_time = start_time + i * delay + duration_time
                )
                pair.drawn_food = [food1]

                food2 = self.reusable_food[0]
                self.reusable_food.remove(food2)
                food2.move_to(
                    new_location = [
                        locations[i][0] + 0.9 * f_scale * math.cos(pair.angle + math.pi / 2),
                        locations[i][1] + 0.9 * f_scale * math.sin(pair.angle + math.pi / 2),
                        f_scale,
                    ],
                    end_time = start_time,
                    start_frame = start_time * FRAME_RATE - 1
                )
                world_const = food2.ref_obj.constraints[0]
                world_const.keyframe_insert(
                    data_path = 'influence',
                    frame = start_time * FRAME_RATE - 1
                )
                world_const.influence = 1
                world_const.keyframe_insert(
                    data_path = 'influence',
                    frame = start_time * FRAME_RATE
                )

                food2.move_to(
                    new_scale = f_scale,
                    start_time = start_time + i * delay,
                    end_time = start_time + i * delay + duration_time
                )
                pair.drawn_food.append(food2)

            else:
                food1 = DrawnFood(
                    object_model = self.food_object_model,
                    location = [
                        locations[i][0] - 0.9 * f_scale * math.cos(pair.angle + math.pi / 2),
                        locations[i][1] - 0.9 * f_scale * math.sin(pair.angle + math.pi / 2),
                        f_scale,
                    ],
                    scale = f_scale,
                    mat = 'color7'
                )

                constraint = food1.ref_obj.constraints.new('CHILD_OF')
                constraint.target = self.ref_obj
                #constraint.use_rotation_x = False
                #constraint.use_rotation_y = False
                #constraint.use_rotation_z = False

                food1.add_to_blender(
                    appear_time = start_time + i * delay,
                    transition_time = duration_time * FRAME_RATE
                )
                pair.drawn_food = [food1]

                food2 = DrawnFood(
                    object_model = self.food_object_model,
                    location = [
                        locations[i][0] + 0.9 * f_scale * math.cos(pair.angle + math.pi / 2),
                        locations[i][1] + 0.9 * f_scale * math.sin(pair.angle + math.pi / 2),
                        f_scale,
                    ],
                    scale = f_scale,
                    mat = 'color7'
                )

                constraint = food2.ref_obj.constraints.new('CHILD_OF')
                constraint.target = self.ref_obj
                #constraint.use_rotation_x = False
                #constraint.use_rotation_y = False
                #constraint.use_rotation_z = False

                food2.add_to_blender(
                    appear_time = start_time + i * delay,
                    transition_time = duration_time * FRAME_RATE
                )
                pair.drawn_food.append(food2)

    def animate_day(self, day = None):
        target_food = None
        #creatures go out
        for cre in day.creatures:
            cre.home_loc = list(cre.drawn_creature.ref_obj.location)
            for entry in cre.days_log:
                if entry['date'] == day.date:
                    target_food = entry['food']
            if target_food != None:
                if cre == target_food.interested_creatures[0]:
                    cre.drawn_creature.walk_to(
                        start_time = self.elapsed_time,
                        end_time = self.elapsed_time + self.phase_durations['creatures_go_out'],
                        new_location = [
                            target_food.location[0] + self.creature_scale * math.cos(target_food.angle),
                            target_food.location[1] + self.creature_scale * math.sin(target_food.angle),
                            cre.drawn_creature.ref_obj.location[2]
                        ],
                        new_angle = [
                            cre.drawn_creature.ref_obj.rotation_euler[0],
                            cre.drawn_creature.ref_obj.rotation_euler[1],
                            target_food.angle - math.pi / 2
                        ]
                    )
                elif cre == target_food.interested_creatures[1]:
                    cre.drawn_creature.walk_to(
                        start_time = self.elapsed_time,
                        end_time = self.elapsed_time + self.phase_durations['creatures_go_out'],
                        new_location = [
                            target_food.location[0] - self.creature_scale * math.cos(target_food.angle),
                            target_food.location[1] - self.creature_scale * math.sin(target_food.angle),
                            cre.drawn_creature.ref_obj.location[2]
                        ],
                        new_angle = [
                            cre.drawn_creature.ref_obj.rotation_euler[0],
                            cre.drawn_creature.ref_obj.rotation_euler[1],
                            target_food.angle + math.pi / 2
                        ]
                    )
                else:
                    raise Warning('Something is wrong with how interested_creatures is assigned')

        self.elapsed_time += self.phase_durations['creatures_go_out'] + self.phase_durations['pause_before_contest']

        #Resolve contests
        dur = self.phase_durations['contest']
        all_halves = []
        for contest in day.contests:
            if contest.outcome == 'share':
                #print("Share on day " + str(contest.date))
                for i in range(2):
                    food = contest.food.drawn_food[i]
                    eater = contest.contestants[i].drawn_creature

                    transfer_food_to_creature(
                        food_bobj = food,
                        creature_bobj = eater,
                        start_time = self.elapsed_time
                    )
                    #Eat animation
                    animate_eating(
                        food = food,
                        eater = eater,
                        start_time = self.elapsed_time,
                        eat_rotation = 30 * math.pi / 180,
                        dur = dur / 2 #If they cooperate, it takes half time
                    )


            elif contest.outcome == 'take':
                #print("Take on day " + str(contest.date))

                loser_index = 0
                taker_index = contest.contestants.index(contest.winner)
                if taker_index == 0:
                    loser_index = 1

                #print(taker_index)
                #print(loser_index)

                taker = contest.contestants[taker_index].drawn_creature
                loser = contest.contestants[loser_index].drawn_creature

                food = contest.food.drawn_food[loser_index]

                halves = []
                for i in range(2):
                    if len(self.reusable_halves) > 1:
                        half = self.reusable_halves[0]
                        self.reusable_halves.remove(half)
                        half.move_to(
                            new_location = food.ref_obj.location,
                            new_scale = 0,
                            new_angle = [0, (-1) ** (i + loser_index) * math.pi / 2, 0],
                            start_frame = self.elapsed_time * FRAME_RATE - 1,
                            end_frame = self.elapsed_time * FRAME_RATE
                        )

                        for j, const in enumerate(half.ref_obj.constraints):
                            const.keyframe_insert(
                                data_path = 'influence',
                                frame = self.elapsed_time * FRAME_RATE - 1
                            )
                            if j == 0:
                                const.influence = 1
                            else:
                                const.influence = 0
                            const.keyframe_insert(
                                data_path = 'influence',
                                frame = self.elapsed_time * FRAME_RATE
                            )

                    else:
                        half = DrawnFood(
                            object_model = self.half_food_object_model,
                            location = food.ref_obj.location,
                            scale = 0,
                            #rotation_euler = [- math.pi / 2 , 0, 0],
                            rotation_euler = [0, (-1) ** (i + loser_index) * math.pi / 2, 0],
                            mat = 'color7'
                        )
                        half.add_to_blender(
                            appear_frame = self.elapsed_time * FRAME_RATE,
                            transition_time = 1
                        )

                        constraint = half.ref_obj.constraints.new('CHILD_OF')
                        constraint.target = self.ref_obj
                        constraint.use_rotation_x = False
                        constraint.use_rotation_y = False
                        constraint.use_rotation_z = False

                    half.move_to(
                        start_frame = self.elapsed_time * FRAME_RATE,
                        end_frame = self.elapsed_time * FRAME_RATE + 1,
                        new_scale = food.ref_obj.scale
                    )

                    halves.append(half)
                    all_halves.append(half)


                food.move_to(
                    start_frame = self.elapsed_time * FRAME_RATE,
                    end_frame = self.elapsed_time * FRAME_RATE + 1,
                    new_scale = 0
                )

                for i, half in enumerate(halves):
                    transfer_food_to_creature(
                        food_bobj = half,
                        creature_bobj = contest.contestants[(taker_index + i) % 2].drawn_creature,
                        start_time = self.elapsed_time
                    )
                    #Eat animation
                    animate_eating(
                        food = half,
                        eater = contest.contestants[(taker_index + i) % 2].drawn_creature,
                        start_time = self.elapsed_time,
                        eat_rotation = (-1) ** ((1 + i) % 2) * 30 * math.pi / 180,
                        dur = dur / 2 #If they cooperate, it takes half time
                    )

                #Other food
                food = contest.food.drawn_food[taker_index]
                eater = contest.contestants[taker_index].drawn_creature

                transfer_food_to_creature(
                    food_bobj = food,
                    creature_bobj = eater,
                    start_time = self.elapsed_time + dur / 2
                )
                #Eat animation
                animate_eating(
                    food = food,
                    eater = eater,
                    start_time = self.elapsed_time + dur / 2,
                    eat_rotation = 30 * math.pi / 180,
                    dur = dur / 2 #If they cooperate, it takes half time
                )

                if self.wiggle == False:
                    loser.wince(
                        start_time = self.elapsed_time + dur / 2,
                        end_time = self.elapsed_time + dur + self.phase_durations['pause_before_home'],
                    )
                    taker.evil_pose(
                        start_time = self.elapsed_time + dur,
                        end_time = self.elapsed_time + dur + self.phase_durations['pause_before_home'],
                    )

            elif contest.outcome == 'fight':
                #print("Take on day " + str(contest.date))

                for cre in contest.contestants:
                    cre.drawn_creature.blob_wave(
                        start_time = self.elapsed_time,
                        duration = dur / 3
                    )
                    if self.wiggle == False:
                        cre.drawn_creature.wince(
                            start_time = self.elapsed_time + dur,
                            end_time = self.elapsed_time + dur + self.phase_durations['pause_before_home'],
                        )

                for j in range(2):
                    food = contest.food.drawn_food[j]
                    halves = []
                    for i in range(2):
                        if len(self.reusable_halves) > 1:
                            half = self.reusable_halves[0]
                            self.reusable_halves.remove(half)
                            half.move_to(
                                new_location = food.ref_obj.location,
                                new_scale = 0,
                                new_angle = [0, (-1) ** (i) * math.pi / 2, 0],
                                start_frame = self.elapsed_time * FRAME_RATE - 1,
                                end_frame = self.elapsed_time * FRAME_RATE
                            )

                            for k, const in enumerate(half.ref_obj.constraints):
                                const.keyframe_insert(
                                    data_path = 'influence',
                                    frame = self.elapsed_time * FRAME_RATE - 1
                                )
                                if k == 0:
                                    const.influence = 1
                                else:
                                    const.influence = 0
                                const.keyframe_insert(
                                    data_path = 'influence',
                                    frame = self.elapsed_time * FRAME_RATE
                                )

                        else:
                            half = DrawnFood(
                                object_model = self.half_food_object_model,
                                location = food.ref_obj.location,
                                scale = 0,
                                #rotation_euler = [- math.pi / 2 , 0, 0],
                                rotation_euler = [0, (-1) ** (i) * math.pi / 2, 0],
                                mat = 'color7'
                            )
                            half.add_to_blender(
                                appear_frame = self.elapsed_time * FRAME_RATE,
                                transition_time = 1
                            )

                            constraint = half.ref_obj.constraints.new('CHILD_OF')
                            constraint.target = self.ref_obj
                            constraint.use_rotation_x = False
                            constraint.use_rotation_y = False
                            constraint.use_rotation_z = False

                        half.move_to(
                            start_frame = self.elapsed_time * FRAME_RATE,
                            end_frame = self.elapsed_time * FRAME_RATE + 1,
                            new_scale = food.ref_obj.scale
                        )

                        halves.append(half)
                        all_halves.append(half)

                    food.move_to(
                        start_frame = self.elapsed_time * FRAME_RATE,
                        end_frame = self.elapsed_time * FRAME_RATE + 1,
                        new_scale = 0
                    )

                    for i, half in enumerate(halves):
                        transfer_food_to_creature(
                            food_bobj = half,
                            creature_bobj = contest.contestants[i % 2].drawn_creature,
                            start_time = self.elapsed_time + dur / 3 + j * dur / 3
                        )
                        #Eat animation
                        animate_eating(
                            food = half,
                            eater = contest.contestants[i % 2].drawn_creature,
                            start_time = self.elapsed_time + dur / 3 + j * dur / 3,
                            eat_rotation = (-1) ** ((i + j) % 2) * 30 * math.pi / 180,
                            dur = dur / 3 #If they cooperate, it takes half time
                        )

            else:
                raise Warning('Unknown contest outcome')

        self.reusable_halves += all_halves
        for food in day.food_objects:
            if len(food.interested_creatures) == 1:
                eater = food.interested_creatures[0].drawn_creature
                for i in range(2):
                    piece = food.drawn_food[i]

                    transfer_food_to_creature(
                        food_bobj = piece,
                        creature_bobj = eater,
                        start_time = self.elapsed_time + i * dur / 2
                    )
                    #Eat animation
                    animate_eating(
                        food = piece,
                        eater = eater,
                        start_time = self.elapsed_time + i * dur / 2,
                        dur = dur / 2, #If they cooperate, it takes half time
                        eat_rotation = (-1) ** i * 30 * math.pi / 180
                    )

        self.elapsed_time += self.phase_durations['contest'] + self.phase_durations['pause_before_home']

        #creatures go home
        for cre in day.creatures:
            cre.drawn_creature.walk_to(
                start_time = self.elapsed_time,
                end_time = self.elapsed_time + self.phase_durations['creatures_go_home'],
                new_location = cre.home_loc,
                new_angle = [
                    cre.drawn_creature.ref_obj.rotation_euler[0],
                    cre.drawn_creature.ref_obj.rotation_euler[1],
                    math.atan2(cre.home_loc[1], cre.home_loc[0]) - math.pi / 2
                ]
            )
        #TODO: update based on phase durations
        self.elapsed_time += self.phase_durations['creatures_go_home'] + self.phase_durations['pause_before_reset']

    def animate_days(
        self,
        start_time = None,
        phase_duration_updates = [],
        graph_mode_changes = {},
        first_animated_day = 0,
        last_animated_day = math.inf,
        graph_only = False
    ):
        self.elapsed_time = start_time
        if last_animated_day == math.inf:
            last_animated_day = self.sim.calendar[-1].date + 1


        for i, day in enumerate(self.sim.calendar):
            if i >= first_animated_day and i < last_animated_day:
                print('Animating day ' + str(i))
                for update in phase_duration_updates:
                    if update[0] == i:
                        for change in update[1]:
                            self.phase_durations[change] = update[1][change]

                update_duration = min(
                    OBJECT_APPEARANCE_TIME / FRAME_RATE,
                    self.phase_durations['day_prep']
                )

                if graph_only == False:
                    self.set_food(
                        start_time = self.elapsed_time,
                        end_time = self.elapsed_time + update_duration,
                        day = day
                    )

                is_first_day = False
                if day.date == first_animated_day:
                    is_first_day = True
                #self.update_agent_scale(day_index = i)

                self.update_creatures(
                    start_time = self.elapsed_time,
                    end_time = self.elapsed_time + update_duration,
                    day = day,
                    is_first_day = is_first_day,
                    graph_only = graph_only
                )

                self.elapsed_time += self.phase_durations['day_prep']

                if graph_only == False:
                    self.animate_day(day = day)

                    update_duration = min(
                        OBJECT_APPEARANCE_TIME / FRAME_RATE,
                        self.phase_durations['food_disappear']
                    )

                    for food in day.food_objects:
                        for d_food in food.drawn_food:
                            d_food.move_to(
                                new_scale = 0,
                                start_time = self.elapsed_time,
                                end_time = self.elapsed_time + update_duration
                            )
                            const = d_food.ref_obj.constraints[-1]
                            if 'blob' in const.target.name:
                                const.keyframe_insert(
                                    data_path = 'influence',
                                    frame = (self.elapsed_time + update_duration) * FRAME_RATE
                                )
                                const.influence = 0
                                const.keyframe_insert(
                                    data_path = 'influence',
                                    frame = (self.elapsed_time + update_duration) * FRAME_RATE + 1
                                )

                            self.reusable_food.append(d_food)

                self.elapsed_time += self.phase_durations['food_disappear']

                '''self.update_creatures(
                    start_time = self.elapsed_time,
                    end_time = self.elapsed_time + update_duration,
                    day = day,
                    updating_next = True
                )'''

        '''update_duration = min(
            OBJECT_APPEARANCE_TIME / FRAME_RATE,
            self.phase_durations['day_prep']
        )'''

        #Show reproductions after last day
        self.update_creatures(
            start_time = self.elapsed_time,
            end_time = self.elapsed_time + update_duration,
            day = self.sim.calendar[int(last_animated_day - 1)],
            updating_next = True,
            graph_only = graph_only
        )
        self.elapsed_time += self.phase_durations['day_prep']

    def add_functions_to_graph(self, bounded_regions = None):
        if TRAIT_MODE == 'binary':
            self.doves_by_day = []
            self.hawks_by_day = []
            for day in self.sim.calendar:
                self.doves_by_day.append(len([x for x in day.creatures if x.fight_chance == 0]))
                self.hawks_by_day.append(len([x for x in day.creatures if x.fight_chance == 1]))

            #Add creatures from final update
            self.doves_by_day.append(len([x for x in self.sim.calendar[-1].next_creatures if x.fight_chance == 0]))
            self.hawks_by_day.append(len([x for x in self.sim.calendar[-1].next_creatures if x.fight_chance == 1]))

            g = self.linked_graph

            for func in [self.doves_by_day, self.hawks_by_day]:
                g.functions.append(func)
                g.functions_coords.append( g.func_to_coords(func_index = -1) )

        elif TRAIT_MODE == 'float':
            funcs = []
            for i in range(11):
                func = []
                for day in self.sim.calendar:
                    func.append(len([x for x in day.creatures if int(x.fight_chance * 10) == i]))
                func.append(len([x for x in self.sim.calendar[-1].next_creatures if int(x.fight_chance * 10) == i]))

                funcs.append(func)

            g = self.linked_graph

            for func in funcs:
                g.functions.append(func)
                g.functions_coords.append( g.func_to_coords(func_index = -1) )

        if bounded_regions == True:
            g.add_all_bounded_regions()
        #print(len(g.functions))

    def update_graph(
        self,
        date = None,
        start_time = None,
        end_time = None
    ):
        if start_time != None:
            start_frame = int(start_time * FRAME_RATE)
        else:
            raise Warning('Need start_time to update graph')
        if end_time != None:
            end_frame = int(end_time * FRAME_RATE)
        else:
            raise Warning('Need end_time to update graph')

        g = self.linked_graph

        if date == 0:
            pass
        else:
            for i in range(len(g.regions_curves)):
                #print(i)
                #print(len(g.regions_curves))
                data = g.regions_curves[i].ref_obj.children[0].data

                data.shape_keys.eval_time = 10 * (date - 1)
                data.shape_keys.keyframe_insert(
                    data_path = 'eval_time',
                    frame = start_frame
                )
                data.shape_keys.eval_time = 10 * date
                data.shape_keys.keyframe_insert(
                    data_path = 'eval_time',
                    frame = end_frame
                )

        if date > g.x_range[1]:
            x_step = g.tick_step[0]
            if date >= 4 * x_step:
                x_step *= 2
            g.change_window(
                start_time = start_frame / FRAME_RATE,
                end_time = end_frame / FRAME_RATE,
                new_x_range = [
                    g.x_range[0],
                    date#g.x_range[1] + 1
                ],
                new_tick_step = [
                    x_step,
                    g.tick_step[1]
                ]
            )

def transfer_food_to_creature(
    food_bobj = None,
    creature_bobj = None,
    start_time = None,
    ground_plane = 'xy'
):
    if food_bobj == None:
        raise Warning('Need food_bobj for transfer_food_to_creatures')
    if creature_bobj == None:
        raise Warning('Need creature_bobj for transfer_food_to_creatures')
    if start_time == None:
        raise Warning('Need start_time for transfer_food_to_creatures')

    d_food = food_bobj
    eater = creature_bobj

    if len(d_food.ref_obj.constraints) > 0:
        world_const = d_food.ref_obj.constraints[0]
        #Change strengths of constraints
        world_const.keyframe_insert(
            data_path = 'influence',
            frame = (start_time) * FRAME_RATE
        )
        #math.floor((start_time) * FRAME_RATE)
        world_const.influence = 0
        world_const.keyframe_insert(
            data_path = 'influence',
            frame = (start_time) * FRAME_RATE + 1
        )

    #Make new child_of constraint binding food to eater
    eater_const = d_food.ref_obj.constraints.new('CHILD_OF')
    eater_const.target = eater.ref_obj
    eater_const.influence = 0



    eater_const.keyframe_insert(
        data_path = 'influence',
        frame = (start_time) * FRAME_RATE
    )
    eater_const.influence = 1
    eater_const.keyframe_insert(
        data_path = 'influence',
        frame = (start_time) * FRAME_RATE + 1
    )

    #Change position of food to work in new reference frame
    d_food.ref_obj.keyframe_insert(
        data_path = 'location',
        frame = (start_time) * FRAME_RATE
    )

    old_loc = d_food.ref_obj.location

    #Very strange way to do this, made by piling shortcuts on top of each other
    #whenever a new case came up.
    #With a bit of thought, could be made more general and understandable.

    if ground_plane == 'xy':
        x = 0
        y = 1
        z = 2
        x_fac = 1
    elif ground_plane == 'xz':
        x = 0
        y = 2
        z = 1
        x_fac = -1

    rel = d_food.ref_obj.location - eater.ref_obj.location
    ang = eater.ref_obj.rotation_euler[z]
    sca = eater.ref_obj.scale
    #The rotation matrix is wonky because the creature bobjects
    #are actually rotated 90 degrees about their x-axis
    #Robust!
    loc_in_new_ref_frame = [
        x_fac * (rel[x] * math.cos(-ang) - rel[y] * math.sin(-ang)) / sca[x],
        rel[z] / sca[z],
        - (rel[x] * math.sin(-ang) + rel[y] * math.cos(-ang)) / sca[y]
    ]
    d_food.ref_obj.location = loc_in_new_ref_frame
    d_food.ref_obj.keyframe_insert(
        data_path = 'location',
        frame = (start_time) * FRAME_RATE + 1
    )

    #correct_scale
    d_food.ref_obj.keyframe_insert(
        data_path = 'scale',
        frame = (start_time) * FRAME_RATE
    )
    for i in range(3):
        d_food.ref_obj.scale[i] /= sca[i]
    d_food.ref_obj.keyframe_insert(
        data_path = 'scale',
        frame = (start_time) * FRAME_RATE + 1
    )
    #correct_rotation
    d_food.ref_obj.keyframe_insert(
        data_path = 'rotation_euler',
        frame = (start_time) * FRAME_RATE
    )
    d_food.ref_obj.rotation_euler = [0, math.pi, 0]
    d_food.ref_obj.keyframe_insert(
        data_path = 'rotation_euler',
        frame = (start_time) * FRAME_RATE + 1
    )

def animate_eating(
    food = None,
    eater = None,
    start_time = None,
    eat_rotation = 0,
    dur = None
):
    if isinstance(eat_rotation, float) or isinstance(eat_rotation, float):
        eat_rotation = [0, 0, eat_rotation]

    eater.move_to(
        new_angle = [
            eater.ref_obj.rotation_euler[0] + eat_rotation[0],
            eater.ref_obj.rotation_euler[1] + eat_rotation[1],
            eater.ref_obj.rotation_euler[2] + eat_rotation[2],
        ],
        start_time = start_time,
        end_time = start_time + dur / 2
    )
    eater.move_to(
        new_angle = [
            eater.ref_obj.rotation_euler[0] - eat_rotation[0],
            eater.ref_obj.rotation_euler[1] - eat_rotation[1],
            eater.ref_obj.rotation_euler[2] - eat_rotation[2],
        ],
        start_time = start_time + dur / 2,
        end_time = start_time + dur
    )

    eater.eat_animation(
        start_frame = (start_time + dur / 2) * FRAME_RATE,
        end_frame = (start_time + dur) * FRAME_RATE,
        decay_frames = dur / 6 * FRAME_RATE
    )
    eater.blob_scoop(
        start_time = start_time,
        duration = dur,
    )
    food.move_to(
        start_time = start_time + dur / 3,
        end_time = start_time + 2 * dur / 3,
        new_location = [-0.05, 0.25, 1]
    )
    food.move_to(
        start_time = start_time + 2 * dur / 3,
        end_time = start_time + dur,
        new_location = [-0.05, 0.125, 0],
        new_scale = [0, 0, 0]
    )

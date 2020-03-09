import imp
import bpy
import mathutils
import math
import statistics
import pickle
import inspect
from copy import deepcopy
from random import random, uniform

import sys
sys.path.append('C:\\Users\\justi\\Documents\\CodeProjects\\Primer\\blender_scripts')
sys.path.append('C:\\Users\\justi\\Documents\\CodeProjects\\Primer\\blender_scripts\\tools')

import bobject
import drawn_world
import tex_bobject
import constants


import clear_blender_data
#import alone doesn't check for changes in cached files
imp.reload(drawn_world)
imp.reload(tex_bobject)

imp.reload(constants)
from constants import *

import svg_bobject
imp.reload(svg_bobject)
from svg_bobject import *

import graph_bobject
imp.reload(graph_bobject)
from graph_bobject import *

import helpers
imp.reload(helpers)
from helpers import *

import table_bobject
imp.reload(table_bobject)

import natural_sim
imp.reload(natural_sim)
from natural_sim import *

sys.path.append('C:\\Users\\justi\\Documents\\CodeProjects\\Primer\\blender_scripts\\video_scenes')

import recurring_assets
imp.reload(recurring_assets)
from recurring_assets import *

import population
imp.reload(population)
from population import *

import gesture
imp.reload(gesture)
from gesture import *

import tex_complex
imp.reload(tex_complex)
from tex_complex import TexComplex

import blobject
imp.reload(blobject)
from blobject import Blobject

import hawk_dove
imp.reload(hawk_dove)
import drawn_contest_world
imp.reload(drawn_contest_world)

import aggression
imp.reload(aggression)

import final_vestibular_animations_text
imp.reload(final_vestibular_animations_text)

import recurring_assets
imp.reload(recurring_assets)

def initialize_blender(total_duration = DEFAULT_SCENE_DURATION, clear_blender = True, vertical = False):
    #clear objects and materials
    #Reading the homefile would likely by faster, but it
    #sets the context to None, which breaks a bunch of
    #other stuff down the line. I don't know how to make the context not None.
    #bpy.ops.wm.read_homefile()
    if clear_blender == True:
        clear_blender_data.clear_blender_data()

    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    scn.cycles.device = 'GPU'
    scn.cycles.samples = SAMPLE_COUNT
    scn.cycles.preview_samples = SAMPLE_COUNT
    scn.cycles.light_sampling_threshold = LIGHT_SAMPLING_THRESHOLD
    scn.cycles.transparent_max_bounces = 40
    scn.render.resolution_percentage = RESOLUTION_PERCENTAGE
    scn.render.use_compositing = False
    scn.render.use_sequencer = False
    scn.render.image_settings.file_format = 'PNG'
    scn.render.tile_x = RENDER_TILE_SIZE
    scn.render.tile_y = RENDER_TILE_SIZE
    scn.render.resolution_x = 1920
    scn.render.resolution_y = 1080
    if vertical == True:
        scn.render.resolution_x = 1080
        scn.render.resolution_y = 1920
    #Apparentlly 16-bit color depth pngs don't convert well to mp4 in Blender.
    #It gets all dark. 8-bit it is.
    #BUT WAIT. I can put stacks of pngs straight into premiere.
    scn.render.image_settings.color_depth = '16'
    scn.render.image_settings.color_mode = 'RGBA'
    scn.cycles.film_transparent = True

    #Set to 60 fps
    bpy.ops.script.execute_preset(
        filepath="C:\\Program Files\\Blender Foundation\\Blender\\2.79\\scripts\\presets\\framerate\\60.py",
        menu_idname="RENDER_MT_framerate_presets"
    )

    #Idfk how to do manipulate the context
    '''for area in bpy.context.screen.areas:
        if area.type == 'TIMELINE':
            bpy.context.area = area
            bpy.context.space_data.show_seconds = True'''

    #The line below makes it so Blender doesn't apply gamma correction. For some
    #reason, Blender handles colors differently from how every other program
    #does, and it's terrible. Why.
    #But this fixes it. Also, the RGB values you see in Blender
    #will be wrong, because the gamma correction is still applied when the color
    #is defined, but setting view_transform to 'Raw' undoes the correction in
    #render.
    scn.view_settings.view_transform = 'Raw'

    scn.gravity = (0, 0, -9.81)

    bpy.ops.world.new()
    world = bpy.data.worlds[-1]
    scn.world = world
    nodes = world.node_tree.nodes
    nodes.new(type = 'ShaderNodeMixRGB')
    nodes.new(type = 'ShaderNodeLightPath')
    nodes.new(type = 'ShaderNodeRGB')
    world.node_tree.links.new(nodes[2].outputs[0], nodes[1].inputs[0])
    world.node_tree.links.new(nodes[3].outputs[0], nodes[2].inputs[0])
    world.node_tree.links.new(nodes[4].outputs[0], nodes[2].inputs[2])
    nodes[4].outputs[0].default_value = COLORS_SCALED[0]

    define_materials()

    #set up timeline
    bpy.data.scenes["Scene"].frame_start = 0
    bpy.data.scenes["Scene"].frame_end = total_duration * FRAME_RATE - 1
    bpy.context.scene.frame_set(0)

    #create camera and light
    bpy.ops.object.camera_add(location = CAMERA_LOCATION, rotation = CAMERA_ANGLE)
    cam = bpy.data.cameras[0]
    #cam.type = 'ORTHO'
    cam.type = 'PERSP'
    cam.ortho_scale = 30

    bpy.ops.object.empty_add(type = 'PLAIN_AXES', location = (0, 0, 100))
    lamp_parent = bpy.context.object
    lamp_parent.name = 'Lamps'

    lamp_height = 35
    bpy.ops.object.lamp_add(type = LAMP_TYPE, location = (0, 0, lamp_height))
    lamp = bpy.context.object
    lamp.parent = lamp_parent
    lamp.matrix_parent_inverse = lamp.parent.matrix_world.inverted()
    lamp.data.node_tree.nodes[1].inputs[1].default_value = 1.57
    #lamp.data.shadow_soft_size = 3

    #Sets view to look through camera.
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            override = bpy.context.copy()
            override['area'] = area
            bpy.ops.view3d.viewnumpad(override, type = 'CAMERA')
            break

def is_scene(obj):
    #print('checking scene')
    #if "TextScene" in str(obj):
    if not inspect.isclass(obj):
        #print('  not class')
        return False
    if not issubclass(obj, Scene):
        print(obj)
        #print('  not subclass of scene')
        return False
    if obj == Scene:
        #print(obj)
        #print('  is scene class itself')
        return False
    return True

def get_total_duration(scenes):
    #scenes is a list of (name, object) pairs
    duration = 0
    for scene in scenes:
        duration += scene[1].duration + DEFAULT_SCENE_BUFFER
    return duration

def get_scene_object_list(script_file):
    pairs = inspect.getmembers(script_file, is_scene)
    #The output of inspect.getmembers is a list of (name, class) pairs.
    #This turns that list into a list of (name, object) pairs
    objects = []
    for pair in pairs:
        objects.append([pair[0], pair[1]()])
    return objects

def tex_test():
    initialize_blender(total_duration = 100)

    message = tex_bobject.TexBobject(
        '\\text{Always}',
        '\\text{Pursue}',
        '\\text{Beauty}',
        '\\text{Always}',
        centered = True,
        scale = 8,
        color = 'color10',
        typeface = 'garamond'
    )
    message.add_to_blender(appear_time = 0)
    message.morph_figure('next', start_time = 1)
    message.morph_figure('next', start_time = 2)
    message.morph_figure('next', start_time = 3)

    #message.disappear(disappear_time = 3.5)

    '''t = tex_bobject.TexBobject(
        '\\curvearrowleft'
    )
    t.add_to_blender(appear_time = 0)

    print_time_report()'''

def marketing():
    scene_end = 12
    initialize_blender(total_duration = scene_end)

    x = 7.64349
    y = -8.71545

    b_blob = import_object(
        'boerd_blob_stern', 'creatures',
        location = [-x, y, 0],
        rotation_euler = [0, 57.4 * math.pi / 180, 0],
        scale = 12,
    )
    b_blob.ref_obj.children[0].children[0].data.resolution = 0.2
    apply_material(b_blob.ref_obj.children[0].children[0], 'creature_color3')
    b_blob.add_to_blender(appear_time = 0)

    y_blob = import_object(
        'boerd_blob_stern', 'creatures',
        rotation_euler = [0, -57.4 * math.pi / 180, 0],
        location = [x, y, 0],
        scale = 12,
    )
    y_blob.ref_obj.children[0].children[0].data.resolution = 0.2
    apply_material(y_blob.ref_obj.children[0].children[0], 'creature_color4')
    y_blob.add_to_blender(appear_time = 0)

    y_blob.blob_wave(
        start_time = 0,
        duration = 12
    )

    comp = tex_bobject.TexBobject(
        '\\text{COMPETITION} \\phantom{blargh}',
        centered = True,
        scale = 4.5,
        location = [0, 5.5, 0],
        color = 'color2'
    )
    comp.add_to_blender(appear_time = 0)

def sample_scene():
    initialize_blender()

    num_colors = 8
    for i in range(num_colors):
        ghost = blobject.Blobject(
            location = [3.5 * i - 12.25, 5, 0],
            mat = 'trans_color' + str(i + 1),
            scale = 2,
            wiggle = True
        )
        mat = ghost.ref_obj.children[0].children[0].material_slots[0].material
        node_tree = mat.node_tree
        node_tree.nodes['Volume Absorption'].inputs[1].default_value = 0.2
        node_tree.nodes['Emission'].inputs[1].default_value = 0.2
        node_tree.nodes['Volume Scatter'].inputs[1].default_value = 0.2

        solid = blobject.Blobject(
            location = [3.5 * i - 12.25, -1, 0],
            mat = 'creature_color' + str(i + 1),
            scale = 2,
            wiggle = True
        )

        text = tex_bobject.TexBobject(
            '\\text{Text!}',
            location = [3.5 * i - 12.25, -6, 0],
            centered = True,
            color = 'color' + str(i + 1),
            scale = 1.5
        )

        ghost.add_to_blender(appear_time = 0)
        solid.add_to_blender(appear_time = 0)
        text.add_to_blender(appear_time = 0)

def draw_scenes_from_file(script_file, clear = True):
    #This function is meant to process many scenes at once.
    #Most scenes end up being large enough where it doesn't make sense to have
    #more than one in blender at once, so this is obsolete and will
    #break if you try to process more than one scene at a time.
    scenes = get_scene_object_list(script_file)
    print(scenes)
    duration = get_total_duration(scenes)
    initialize_blender(total_duration = duration, clear_blender = clear)

    frame = 0
    for scene in scenes:
        execute_and_time(
            scene[0], #This is just a string
            scene[1].play()
        )
        #frame += scene[1].duration + DEFAULT_SCENE_BUFFER

    #Hide empty objects from render, for speed
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':
            obj.hide_render = True
    #Doesn't change much, since most empty objects are keyframed handles for
    #other objects.

    print_time_report()

def make_blob_with_actions_for_unity():
    #initialize_blender()

    actual_blob = bpy.data.objects['blob']

    blobj = blobject.Blobject(
        upright = True,
        name = 'blobject_ref_obj',
        #wiggle = True
    )

    #trash = blobj.objects[0]

    blobj.objects[0] = actual_blob
    actual_blob.parent = blobj.ref_obj

    #print()
    #print(blob.__dict__)
    #print()

    '''blob.add_to_blender(
        animate = False,
        unhide = False
    )'''

    '''blobj.evil_pose(
        start_time = 0,
        end_time = 4
    )'''
    blobj.hold_object(
        start_time = 0,
        end_time = 2
    )

def test():
    #initialize_blender()

    def sim_test():
        print('Initial bimodal distribution')

        food_counts_to_try = [
            #37,
            #37,
            #37,
            #37,
            #37,
            #37,
            #37,
            #37,
            #37,
            #50,
            61,
            #61,
            #61,
            #61,
            #61,
            #61,
            #61,
            #1,
            #61,
            #61,
            #61,
            #100,
            #150,
            #200,
            #300,
            #400,
            #500,
            #600,
            #700,
            #800,
            #900,
            #1999
        ]
        nums_days_to_try = [
            #2,
            #10,
            #11,
            #12,
            #13,
            #14,
            #15,
            #16,
            #17,
            #18,
            #19,
            #20,
            #30,
            #40,
            #50,
            #60,
            #70,
            #80,
            #90,
            10000,
            #150,
            #200,
            #300,
            #400,
            #500,
            #600,
            #700,
            #800,
            #900,
            #999,
            #1999
        ]
        num_samples = 1
        quantile_count = 10


        #table_type = 'avgs_with_food_count_and_time'
        table_type = 'show_distribution'

        #Table where rows are food counts and columns are day counts
        #Each cell show mean and stddev of samples
        if table_type == 'avgs_with_food_count_and_time':
            table_headings = '{0: <4}'.format('') + ' | '
            for num in nums_days_to_try:
                table_headings += '{0: ^13}'.format(num) + ' | '
            print('Food v, days >')
            print(table_headings)
            print('-' * len(table_headings))
        elif table_type == 'show_distribution':
            table_headings = '{0: <4}'.format('') + ' | '
            for i in range(quantile_count):
                table_headings += '{0: ^5}'.format(i) + ' | '
            print('Sample v, Quantiles >')
            print(table_headings)
            print('-' * len(table_headings))


        for food_count in food_counts_to_try:
            samples = []
            for j in range(num_samples):
                sample_results = []

                num_creatures = 2 * food_count
                initial_creatures = []
                for k in range(num_creatures):
                    if k == num_creatures - 1: #% 2 == 0:
                        cre = hawk_dove.Creature(
                            fight_chance = 1
                        )
                    else:
                        cre = hawk_dove.Creature(
                            fight_chance = 0
                        )
                    '''cre = hawk_dove.Creature(
                        #fight_chance = 0.2
                        fight_chance = round(k / num_creatures, 1)
                    )'''
                    initial_creatures.append(cre)

                world = hawk_dove_basic.World()#food_count = food_count, initial_creatures = initial_creatures)

                num_days = nums_days_to_try[-1]
                for i in range(num_days):
                    world.new_day()
                    #print('Done simming day ' + str(i))

                #print()
                for day in world.calendar:
                    #print('f_hawks: ' + str(len([x for x in day.creatures if x.fight_chance == 1]) / \
                    #                        (len([x for x in day.creatures if x.fight_chance == 0]) + len([x for x in day.creatures if x.fight_chance == 1])))
                    #)
                    #print('Num hawks: ' + str(len([x for x in day.creatures if x.fight_chance == 1])))
                    #print('num    : ' + str(len(day.creatures)))
                    #print()

                    if table_type == 'avgs_with_food_count_and_time':
                        avg = statistics.mean([x.fight_chance for x in day.creatures])
                        if day.date + 1 in nums_days_to_try:
                            sample_results.append(avg)
                    elif table_type == 'show_distribution':
                        if day.date + 1 in nums_days_to_try:
                            sample_results = (
                                [x.fight_chance for x in day.creatures]
                            )

                    #print("Average fight chance: " + str(avg))

                    #print('Num shares: ' + str(len(day.morning_contests) + len(day.afternoon_contests)))
                    #contests = day.morning_contests + day.afternoon_contests
                    #shares = [x for x in contests if x.outcome == 'share']
                    #takes = [x for x in contests if x.outcome == 'take']
                    #fights = [x for x in contests if x.outcome == 'fight']
                    #print('Num shares: ' + str(len(shares)))
                    #print('Num takes: ' + str(len(takes)))
                    #print('Num fights: ' + str(len(fights)))
                    #for food in day.food_objects:
                    #    print('Eaten = ' + str(food.eaten_time) + ' Creatures = ' + str(food.interested_creatures))
                    #print()

                samples.append(sample_results)

            '''print()
            for sample in samples:
                to_print = ["{0:.2f}".format(round(x, 2)) for x in sample]
                print(to_print)
            print()'''

            if table_type == 'avgs_with_food_count_and_time':
                results_str = '{0: <4}'.format(food_count) + ' | '
                for i in range(len(nums_days_to_try)):
                    samples_at_day = []
                    for sample in samples:
                        samples_at_day.append(sample[i])

                    results_str += "{0:.2f}".format(round(statistics.mean(samples_at_day),2))
                    if len(samples_at_day) > 1:
                        results_str += ' +/- ' + \
                                    "{0:.2f}".format(round(statistics.stdev(samples_at_day),2))

                    results_str += ' | '

            elif table_type == 'show_distribution':
                #print(samples)
                for sample in samples:
                    results_str = '{0: <4}'.format(food_count) + ' | '
                    for i in range(quantile_count + 1): #1 to catch 100%
                        num_in_quantile = 0
                        for cre_fight_chance in sample: #Good naming! ...
                            if cre_fight_chance < (i + 1) / quantile_count and \
                               cre_fight_chance >= i / quantile_count:
                                num_in_quantile += 1

                        results_str += '{0: ^5}'.format(num_in_quantile) + \
                                            ' | '

                    print(results_str)

            if table_type == 'avgs_with_food_count_and_time':
                print(results_str)

    #sim_test()

    def animation_test():
        world = 'hawks_only_10'

        drawn_world = drawn_contest_world.DrawnWorld(
            sim = world,
            loud = True
        )

        #world = hawk_dove.World(food_count = 61)
        world = drawn_world.sim
        #sys.setrecursionlimit(10000)
        '''num_days = 70

        for i in range(num_days):
            save = False
            if i == num_days - 1:
                save = True
            world.new_day(save = save)'''

        drawn_world.add_to_blender(appear_time = 1)
        drawn_world.animate_days(
            start_time = 2,
            first_animated_day = 0,
            last_animated_day = 5
        )

    #animation_test()

    def walk_to_test():
        bleb = blobject.Blobject(
            scale = 4,
            location = [-8, 0, 0],
            rotation_euler = [math.pi / 2, 0, 0]
        )

        bleb.add_to_blender()

        bleb.walk_to(
            new_location = [8, 0, 0],
            new_angle = [math.pi / 2, 0, - math.pi / 2],
            start_time = 3,
            end_time = 5
        )

    #walk_to_test()


    initialize_blender()

    def func0(x):
        return 4 + x / 5 + 3 * math.sin(x)

    def func1(x):
        return 4 + x / 5 + 3 * math.sin(2 * x)

    graph = graph_bobject.GraphBobject(
        func0,
        func1,
        centered = True
    )

    #Times in seconds
    graph.add_to_blender(appear_time = 0) #Animate appearance of axes and labels
    graph.animate_function_curve(start_time = 1, end_time = 2) #Animate drawing of curve
    graph.morph_curve(1, start_time = 3) #Change curve to different function. First arg is destination function index
    graph.change_window( #Animate change of window with same function.
        new_x_range = [0, 15],
        new_y_range = [0, 20],
        new_tick_step = [5, 5],
        start_time = 5
    )

def main():
    """Use this as a test scene"""
    #tex_test()
    """"""
    #initialize_blender()

    #circle_grid()
    #test()
    make_blob_with_actions_for_unity()
    #draw_scenes_from_file(final_vestibular_animations_anatomy, clear = False)
    #draw_scenes_from_file(final_vestibular_animations_text)

    print_time_report()
    finish_noise()

if __name__ == "__main__":
    try:
        main()
    except:
        print_time_report()
        finish_noise(error = True)
        raise()

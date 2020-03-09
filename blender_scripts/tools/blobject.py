import imp

import bobject
imp.reload(bobject)
from bobject import Bobject

#import helpers
from helpers import *

class Blobject(Bobject):
    def __init__(self, mat = 'creature_color3', **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'blob'

        file = 'boerd_blob'
        if 'upright' in kwargs and kwargs['upright'] == True:
            file = 'blob'

        #returns a bobject
        blob = import_object(
            file, 'creatures',
            **kwargs
        )
        #Initialize with blob's ref_obj as a subbobject
        super().__init__(objects = [blob.ref_obj.children[0]], **kwargs)
        apply_material(self.ref_obj.children[0].children[0], mat)

        if self.get_from_kwargs('mouth', False):
            for child in self.ref_obj.children[0].children:
                if 'Mouth' in child.name:
                    self.mouth = child
                    break
                if 'mouth' in child.name:
                    self.mouth = child
                    break

            self.mouth.location = [-0.04, 0.36, 0.40609]
            self.mouth.rotation_euler = [
                -8.91 * math.pi / 180,
                -0.003 * math.pi / 180,
                -3.41 * math.pi / 180,
            ]
            self.mouth.scale = [
                0.487,
                0.719,
                0.398
            ]

    def walk_to(
        self,
        start_time = None,
        end_time = None,
        new_location = None,
        new_angle = None,
        prep_frac = 0.1,
        turn_frac = 0.2
    ):
        if start_time == None:
            raise Warning('Need start time for walk_to')
        if end_time == None:
            end_time = start_time + OBJECT_APPEARANCE_TIME / FRAME_RATE
        duration = end_time - start_time

        if prep_frac > 0.5:
            raise Warning('prep_frac cannot be greater than 0.5')
        if turn_frac > 0.5:
            raise Warning('turn_frac cannot be greater than 0.5')

        if new_location == None:
            raise Warning('Need new_location for walk_to')

        if new_angle == None:
            new_angle = list(self.ref_obj.rotation_euler)

        vector = add_lists_by_element(
            new_location,
            self.ref_obj.location,
            subtract = True
        )

        #I'm going to cheat on my facing-rotations and just do the most common cases

        #Ground is xz-plane case
        if self.ref_obj.rotation_euler[0] == 0:
            heading_angle = [
                0,
                math.atan2(vector[0], vector[2]),
                0,
            ]
            heading_angle[1] = make_angles_within_pi(
                angle_to_change = heading_angle[1],
                reference_angle = self.ref_obj.rotation_euler[1]
            )
            new_angle[1] = make_angles_within_pi(
                angle_to_change = new_angle[1],
                reference_angle = heading_angle[1]
            )

        #Ground is xy-plane case
        elif abs(self.ref_obj.rotation_euler[0] - math.pi / 2) < 0.001:
            heading_angle = [
                math.pi / 2,
                0,
                math.atan2(vector[1], vector[0]) + math.pi / 2,
            ]
            heading_angle[2] = make_angles_within_pi(
                angle_to_change = heading_angle[2],
                reference_angle = self.ref_obj.rotation_euler[2]
            )

            new_angle[2] = make_angles_within_pi(
                angle_to_change = new_angle[2],
                reference_angle = heading_angle[2]
            )

        else:
            print(self.ref_obj.rotation_euler[0])
            print(math.pi / 2)
            raise Warning('walk_to not defined for this starting orientation')



        self.move_to(
            new_angle = heading_angle,
            start_time = start_time,
            end_time = start_time + duration * turn_frac
        )
        self.move_to(
            new_location = new_location,
            start_time = start_time + duration * prep_frac,
            end_time = end_time - duration * prep_frac,
        )
        self.move_to(
            new_angle = new_angle,
            start_time = end_time - duration * turn_frac,
            end_time = end_time
        )

    def move_head(
        self,
        rotation_quaternion = None,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for move_head')
        if rotation_quaternion == None:
            raise Warning('Need angle for move_head')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        head.rotation_quaternion = rotation_quaternion
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_time != None:
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            head.rotation_quaternion = initial
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )

    def add_beard(
        self,
        mat = None,
        low_res = False,
        start_time = -1,
        duration = OBJECT_APPEARANCE_TIME / FRAME_RATE
    ):
        has_beard_already = False
        for obj in self.ref_obj.children[0].children:
            if 'beard' in obj.name:
                has_beard_already = True

        if has_beard_already == False:
            which_beard = 'beard'
            if low_res == True:
                which_beard = 'beard_low_res'

            beard = import_object(
                which_beard, 'misc',
                location = [0.86383, -1.79778, 0.29876],
                rotation_euler = [-40.8 * math.pi / 180, 68.3 * math.pi / 180, -5.77 * math.pi / 180],
                scale = [1.377, 1.377, 0.685],
                name = 'beard'
            )
            beard.ref_obj.parent = self.ref_obj.children[0]
            beard.ref_obj.parent_bone = self.ref_obj.children[0].pose.bones["bone_neck"].name
            beard.ref_obj.parent_type = 'BONE'
            beard.add_to_blender(appear_time = start_time, transition_time = duration * FRAME_RATE)

            self.beard = beard

            if mat is not None:
                apply_material(beard.ref_obj.children[0], mat)

    def hold_gift(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for hold_gift')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        self.hold_object(
            start_time = start_time,
            end_time = end_time,
            attack = attack,
            decay = decay
        )

        gift = import_object(
            'gift_white', 'misc',
            rotation_euler = [-math.pi / 2, 0, 0],
            scale = 0.28
        )
        gift.add_to_blender(
            appear_time = start_time,
            transition_time = attack * FRAME_RATE
        )
        gift.ref_obj.parent = self.ref_obj
        gift.move_to(
            new_location = [0, 0, 0.8],
            start_time = start_time,
            end_time = start_time + attack
        )

        if end_time != None:
            gift.move_to(
                new_location = [0, 0, 0],
                new_scale = 0,
                start_time = end_time - decay,
                end_time = end_time
            )

    def blob_wave(
        self,
        start_time = 0,
        duration = 0,
        end_pause_duration = 0
    ):
        start_frame = start_time * FRAME_RATE
        end_pause_frames = end_pause_duration * FRAME_RATE
        if duration == 0:
            duration = 1
        duration_frames = duration * FRAME_RATE

        wave_cycle_length = min(8, duration_frames / 2)
        cycle_error = math.floor(wave_cycle_length / 2)
        num_wave_cycles = math.floor(duration_frames / wave_cycle_length)
        duration_frames = num_wave_cycles * wave_cycle_length

        l_arm_up_z = 1
        l_arm_down_z = -1
        l_arm_out_y = 3
        l_arm_out_x = 0.5
        r_arm_up_z = -1
        r_arm_down_z = 1
        r_arm_out_y = -5

        #These labels are from the point of view of the blob, which is opposite
        #from how they're labeled in the template .blend file. Huzzah.
        l_arm = None
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                l_arm = child.pose.bones[1]
                r_arm = child.pose.bones[2]

        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = deepcopy(l_arm.rotation_quaternion)
        l_arm.rotation_quaternion[1] = l_arm_out_x
        l_arm.rotation_quaternion[2] = l_arm_out_y
        l_arm.rotation_quaternion[3] = l_arm_down_z
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + wave_cycle_length + uniform(-cycle_error, cycle_error)
        )

        #waves
        for i in range(1, num_wave_cycles - 1): #last one gets overridden
            if i % 2 == 1:
                l_arm.rotation_quaternion[3] = l_arm_up_z
            if i % 2 == 0:
                l_arm.rotation_quaternion[3] = l_arm_down_z
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + wave_cycle_length + uniform(-cycle_error, cycle_error) + i * wave_cycle_length
            )

        #And back
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames - wave_cycle_length  + uniform(-cycle_error, cycle_error)
        )
        #if end_pause_frames != 0:
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames - wave_cycle_length + end_pause_frames
        )
        l_arm.rotation_quaternion = initial_angle
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames + end_pause_frames
        )

        #Right arm
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = deepcopy(r_arm.rotation_quaternion)
        r_arm.rotation_quaternion[2] = r_arm_out_y
        r_arm.rotation_quaternion[3] = r_arm_down_z
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + wave_cycle_length + uniform(-cycle_error, cycle_error)
        )

        #waves
        for i in range(1, num_wave_cycles - 1):
            if i % 2 == 1:
                r_arm.rotation_quaternion[3] = r_arm_up_z
            if i % 2 == 0:
                r_arm.rotation_quaternion[3] = r_arm_down_z
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + wave_cycle_length + uniform(-cycle_error, cycle_error) + i * wave_cycle_length
            )

        #And back
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames - wave_cycle_length + uniform(-cycle_error, cycle_error)
        )
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames - wave_cycle_length + end_pause_frames
        )
        r_arm.rotation_quaternion = initial_angle
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames + end_pause_frames
        )

    def blob_scoop(
        self,
        start_time = 0,
        duration = 0,
        top_pause_time = 0,
        attack = 0.5,
        decay = 0.5
    ):
        #This function only works for blob creatures. Maybe they deserve their
        #own subclass of bobject.
        start_frame = start_time * FRAME_RATE
        duration_frames = (duration) * FRAME_RATE
        if duration < 1.5:
            attack = duration / 3
            decay = duration / 3
        attack_frames = attack * FRAME_RATE
        decay_frames = decay * FRAME_RATE

        l_arm_up_z = -2.7
        l_arm_down_z = 3
        l_arm_out_y = -7.6
        l_arm_forward_x = -3


        r_arm_up_z = -3.6
        r_arm_down_z = 1.8
        r_arm_out_y = -12.7
        r_arm_forward_x = -2.2

        #These labels are from the point of view of the blob, which is opposite
        #from how they're labeled in the template .blend file. Huzzah.
        l_arm = None
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                l_arm = child.pose.bones[1]
                r_arm = child.pose.bones[2]

        #Left arm out
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = deepcopy(l_arm.rotation_quaternion)
        l_arm.rotation_quaternion[1] = l_arm_forward_x
        l_arm.rotation_quaternion[2] = l_arm_out_y
        l_arm.rotation_quaternion[3] = l_arm_down_z
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #scoop
        l_arm.rotation_quaternion[3] = l_arm_up_z
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + 2 * attack_frames
        )
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames - decay_frames
        )

        #And back
        l_arm.rotation_quaternion = initial_angle
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames
        )

        #Right arm
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = deepcopy(r_arm.rotation_quaternion)
        r_arm.rotation_quaternion[1] = r_arm_forward_x
        r_arm.rotation_quaternion[2] = r_arm_out_y
        r_arm.rotation_quaternion[3] = r_arm_down_z
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #scoop
        r_arm.rotation_quaternion[3] = r_arm_up_z
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + 2 * attack_frames
        )
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames - decay_frames
        )

        #And back
        r_arm.rotation_quaternion = initial_angle
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + duration_frames
        )

    def evil_pose(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for evil pose')
        if end_time == None:
            raise Warning('Need end time for evil pose')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        new_action = bpy.data.actions.new('Evil Pose')
        if self.ref_obj.children[0].animation_data.action == None:
            self.ref_obj.children[0].animation_data_create()
        self.ref_obj.children[0].animation_data.action = new_action

        #Blob's left arm up = [1, -2.5, -8.1, -1.5]
        #Blob's right arm up = [1, 0.4, -36.6, -9]

        #These labels are from the point of view of the blob, which is opposite
        #from how they're labeled in the template .blend file. Huzzah.
        l_arm = None
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                l_arm = child.pose.bones['bone_arm.r']
                r_arm = child.pose.bones['bone_arm.l']

        #Left arm up
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = list(l_arm.rotation_quaternion)
        l_arm.rotation_quaternion = [1, -2.5, -8.1, -1.5]
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_frame != None:
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            l_arm.rotation_quaternion = initial_angle
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )

        #Right arm up
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = list(r_arm.rotation_quaternion)
        r_arm.rotation_quaternion = [1, -2.5, -8.1, -1.5]
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_frame != None:
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            r_arm.rotation_quaternion = initial_angle
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )


        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)

        head_back = [1, -0.1, 0, 0.1]
        head_back_left = [1, -0.1, 0.1, 0.1]
        head_back_right = [1, -0.1, -0.1, 0.1]

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        head.rotation_quaternion = head_back
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )


        #Shakes
        still_time = end_frame - start_frame - attack_frames - decay_frames
        if still_time >= 5 * OBJECT_APPEARANCE_TIME:
            still_time = still_time - 2 * OBJECT_APPEARANCE_TIME

            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3
            )
            head.rotation_quaternion = head_back_left
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3 + OBJECT_APPEARANCE_TIME
            )

            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 1 * OBJECT_APPEARANCE_TIME
            )
            head.rotation_quaternion = head_back_right
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 2 * OBJECT_APPEARANCE_TIME
            )


        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

        #Eyes
        '''self.angry_eyes(
            start_time = start_time,
            end_time = end_time,
            attack = attack,
            decay = decay
        )'''

        #Mouth
        self.eat_animation(
            start_frame = start_frame,
            end_frame = end_frame,
            attack_frames = attack_frames,
            decay_frames = decay_frames
        )

    def cheer(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for cheer')
        if end_time == None:
            raise Warning('Need end time for cheer')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        self.blob_wave(
            start_time = start_time,
            duration = end_time - start_time
        )

        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)
        head_back = [1, -0.1, 0, 0.1]
        #head_back_left = [1, -0.1, 0.1, 0.1]
        #head_back_right = [1, -0.1, -0.1, 0.1]
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        head.rotation_quaternion = head_back
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

        #Mouth
        self.eat_animation(
            start_frame = start_frame,
            end_frame = end_frame,
            attack_frames = attack_frames,
            decay_frames = decay_frames
        )

    def angry_eyes(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None,
        left = True,
        right = True
    ):
        if start_time == None:
            raise Warning('Need start time for angry_eyes()')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Eyes
        #For some ungodly reason, I can't just refer to them by name directly
        #bpy.data.objects['eye_l'] #
        #bpy.data.objects['eye_r'] #

        left_eye = self.ref_obj.children[0].children[-2]
        right_eye = self.ref_obj.children[0].children[-3]

        '''new_action = bpy.data.actions.new('angry_eyes')
        if left_eye.animation_data.action == None:
            left_eye.animation_data_create()
        left_eye.animation_data.action = new_action
        if right_eye.animation_data.action == None:
            right_eye.animation_data_create()
        right_eye.animation_data.action = new_action'''


        eyes = []
        if left == True:
            eyes.append(left_eye)
        if right == True:
            eyes.append(right_eye)
        for eye in eyes:
                key = eye.data.shape_keys.key_blocks['Key 1']
                initial_val = deepcopy(key.value)
                key.keyframe_insert(data_path = 'value', frame = start_frame)
                key.value = 1
                key.keyframe_insert(data_path = 'value', frame = start_frame + attack_frames)
                if end_frame != None:
                    key.keyframe_insert(data_path = 'value', frame = end_frame - decay_frames)
                    key.value = initial_val
                    key.keyframe_insert(data_path = 'value', frame = end_frame)

    def normal_eyes(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for normal_eyes()')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Eyes
        eyes = [
            self.ref_obj.children[0].children[-2],
            self.ref_obj.children[0].children[-3],
        ]
        for eye in eyes:
                key = eye.data.shape_keys.key_blocks['Key 1']
                initial_val = key.value
                key.keyframe_insert(data_path = 'value', frame = start_frame)
                key.value = 0
                key.keyframe_insert(data_path = 'value', frame = start_frame + attack_frames)
                if end_frame != None:
                    key.keyframe_insert(data_path = 'value', frame = end_frame - decay_frames)
                    key.value = initial_val
                    key.keyframe_insert(data_path = 'value', frame = end_frame)

    def surprise_eyes(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for normal_eyes()')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Eyes
        eyes = [
            self.ref_obj.children[0].children[-2],
            self.ref_obj.children[0].children[-3],
        ]
        for eye in eyes:

            #key = eye.data.shape_keys.key_blocks['Key 1']
            initial_val = copy(eye.scale)
            eye.keyframe_insert(data_path = 'scale', frame = start_frame)
            eye.scale = [1.2, 1.2, 1.2]
            eye.keyframe_insert(data_path = 'scale', frame = start_frame + attack_frames)
            if end_frame != None:
                eye.keyframe_insert(data_path = 'scale', frame = end_frame - decay_frames)
                eye.scale = initial_val
                eye.keyframe_insert(data_path = 'scale', frame = end_frame)

    #Not implemented. Just evil pose for now
    def shrug(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for evil pose')
        if end_time == None:
            raise Warning('Need end time for evil pose')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE


        #Blob's left arm up = [0.304, 0.034, 0.409, 0.011]
        #Blob's right arm up = [0.304, 0.034, 0.409, 0.011]

        #These labels are from the point of view of the blob, which is opposite
        #from how they're labeled in the template .blend file. Huzzah.
        l_arm = None
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                l_arm = child.pose.bones[1]
                r_arm = child.pose.bones[2]

        #Left arm up
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = list(l_arm.rotation_quaternion)
        l_arm.rotation_quaternion = [1, -2.5, -8.1, -1.5]
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_frame != None:
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            l_arm.rotation_quaternion = initial_angle
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )

        #Right arm up
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = list(r_arm.rotation_quaternion)
        r_arm.rotation_quaternion = [1, -2.5, -8.1, -1.5]
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_frame != None:
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            r_arm.rotation_quaternion = initial_angle
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )


        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)

        head_back = [1, -0.1, 0, 0.1]
        head_back_left = [1, -0.1, 0.1, 0.1]
        head_back_right = [1, -0.1, -0.1, 0.1]

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        head.rotation_quaternion = head_back
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )


        #Shakes
        still_time = end_frame - start_frame - attack_frames - decay_frames
        if still_time >= 5 * OBJECT_APPEARANCE_TIME:
            still_time = still_time - 2 * OBJECT_APPEARANCE_TIME

            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3
            )
            head.rotation_quaternion = head_back_left
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3 + OBJECT_APPEARANCE_TIME
            )

            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 1 * OBJECT_APPEARANCE_TIME
            )
            head.rotation_quaternion = head_back_right
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 2 * OBJECT_APPEARANCE_TIME
            )


        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

        #Eyes
        eyes = [
            self.ref_obj.children[0].children[-2],
            self.ref_obj.children[0].children[-3],
        ]
        for eye in eyes:
                key = eye.data.shape_keys.key_blocks['Key 1']
                key.keyframe_insert(data_path = 'value', frame = start_frame)
                key.value = 1
                key.keyframe_insert(data_path = 'value', frame = start_frame + attack_frames)
                if end_frame != None:
                    key.keyframe_insert(data_path = 'value', frame = end_frame - decay_frames)
                    key.value = 0
                    key.keyframe_insert(data_path = 'value', frame = end_frame)

        #Mouth
        self.eat_animation(
            start_frame = start_frame,
            end_frame = end_frame,
            attack_frames = attack_frames,
            decay_frames = decay_frames
        )

    def hello(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for blob hello')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE / 2
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE / 2
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE / 2
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE / 2
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        new_action = bpy.data.actions.new('Hello')
        if self.ref_obj.children[0].animation_data.action == None:
            self.ref_obj.children[0].animation_data_create()
        self.ref_obj.children[0].animation_data.action = new_action

        r_arm_up_z = -1.5
        r_arm_down_z = 1
        r_arm_out_y = -5

        #These labels are from the point of view of the blob, which is opposite
        #from how they're labeled in the template .blend file. Huzzah.
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                r_arm = child.pose.bones['bone_arm.r']


        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )

        #Right wave
        initial_angle = list(r_arm.rotation_quaternion)

        wave_cycle_length_min = 12
        waving_duration = end_frame - start_frame - attack_frames - decay_frames
        num_wave_cycles = math.floor(waving_duration / wave_cycle_length_min)
        wave_cycle_length = waving_duration / num_wave_cycles

        for i in range(num_wave_cycles):
            r_arm.rotation_quaternion = [
                initial_angle[0],
                initial_angle[1],
                r_arm_out_y,
                r_arm_down_z
            ]
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + wave_cycle_length * i
            )
            r_arm.rotation_quaternion = [
                initial_angle[0],
                initial_angle[1],
                r_arm_out_y,
                r_arm_up_z
            ]
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + wave_cycle_length * (i + 0.5)
            )

        #And back
        if end_frame != None:
            r_arm.rotation_quaternion = [
                initial_angle[0],
                initial_angle[1],
                r_arm_out_y,
                r_arm_down_z
            ]
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            r_arm.rotation_quaternion = initial_angle
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )


        #Head
        head = self.ref_obj.children[0].pose.bones['bone_neck']
        initial = list(head.rotation_quaternion)

        head_tilt = [1, -0.1, 0, -0.1]

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        head.rotation_quaternion = head_tilt
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

    def wince(
        self,
        start_time = None,
        end_time = None,
        period = OBJECT_APPEARANCE_TIME,
        non_uniform = False,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for wince')

        if end_time == None:
            raise Warning('Need end time for wince')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        default_attack = OBJECT_APPEARANCE_TIME / 2

        if attack == None:
            if end_time == None:
                attack = default_attack / FRAME_RATE
            elif end_time - start_time > 2:
                attack = default_attack / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = default_attack / FRAME_RATE
            elif end_time - start_time > 2:
                decay = default_attack / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)

        head_down = [1, 0.2, 0.1, -0.5]
        head_down_left = [1, 0, 0.4, -0.5]
        head_down_right = [1, 0, -0.1, -0.5]

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        head.rotation_quaternion = head_down
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )


        #Shakes
        still_time = end_frame - start_frame - attack_frames - decay_frames
        num_shakes = math.floor(2 * still_time / (period * FRAME_RATE))
        for i in range(num_shakes):
            '''head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3
            )'''
            if i % 2 == 0:
                head.rotation_quaternion = head_down_left
            else:
                head.rotation_quaternion = head_down_right
            variation = 0
            if non_uniform == True:
                variation = uniform(-1, 1) * 0.1 * period
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames \
                    + (1 + i) * period * FRAME_RATE / 2 + variation
            )

            '''head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 1 * OBJECT_APPEARANCE_TIME
            )
            head.rotation_quaternion = head_back_right
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 2 * OBJECT_APPEARANCE_TIME
            )'''



        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        if decay_frames > OBJECT_APPEARANCE_TIME:
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - OBJECT_APPEARANCE_TIME
            )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

        #Eyes
        eyes = [
            self.ref_obj.children[0].children[-2],
            self.ref_obj.children[0].children[-3],
        ]
        for eye in eyes:
            init_eye_scale = list(eye.scale)
            init_eye_rot = list(eye.rotation_euler)

            eye.keyframe_insert(data_path = 'scale', frame = start_frame)
            eye.scale = [1, 0.3, 0.3]
            eye.keyframe_insert(data_path = 'scale', frame = start_frame + attack_frames)
            #Override blinks
            i = 0
            while start_frame + attack_frames + i <= end_frame - decay_frames:
                eye.keyframe_insert(data_path = 'scale', frame = int(start_frame + attack_frames + i))
                i += 1


            eye.keyframe_insert(data_path = 'scale', frame = end_frame - decay_frames)
            eye.scale = init_eye_scale
            eye.keyframe_insert(data_path = 'scale', frame = end_frame)



            eye.keyframe_insert(data_path = 'rotation_euler', frame = start_frame)
            if eye == eyes[1]:
                eye.rotation_euler = [0, -20 * math.pi / 180, 0]
            else:
                eye.rotation_euler = [0, 20 * math.pi / 180, 0]
            eye.keyframe_insert(data_path = 'rotation_euler', frame = start_frame + attack_frames)
            eye.keyframe_insert(data_path = 'rotation_euler', frame = end_frame - decay_frames)
            eye.rotation_euler = init_eye_rot
            eye.keyframe_insert(data_path = 'rotation_euler', frame = end_frame)

        '''leye = self.ref_obj.children[0].pose.bones[5]
        reye = self.ref_obj.children[0].pose.bones[6]

        for eye_bone in [leye, reye]:
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = start_frame)
            if eye_bone == leye:
                eye.rotation_quaternion = [1, 0, 0.1, 0]
            else:
                eye.rotation_quaternion = [1, 0, -0.1, 0]
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = start_frame + attack_frames)
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = end_frame - decay_frames)
            eye_bone.rotation_quaternion = init_eye_rot
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = end_frame)'''

    def nod_yes(
        self,
        start_time = None,
        end_time = None,
        attack = 0,
        decay = 0
    ):
        if start_time == None:
            raise Warning('Need start time for wince')

        if end_time == None:
            raise Warning('Need end time for wince')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        default_attack = OBJECT_APPEARANCE_TIME / 2

        if attack == None:
            if end_time == None:
                attack = default_attack / FRAME_RATE
            elif end_time - start_time > 2:
                attack = default_attack / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = default_attack / FRAME_RATE
            elif end_time - start_time > 2:
                decay = default_attack / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)

        head_up = [1, 0.1, 0, -0.1]
        head_down = [1, 0, 0, 0.05]

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )

        #Shakes
        still_time = end_frame - start_frame - attack_frames - decay_frames
        num_shakes = math.floor(2 * still_time / OBJECT_APPEARANCE_TIME)
        for i in range(num_shakes):
            '''head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3
            )'''
            if i % 2 == 0:
                head.rotation_quaternion = head_up
            else:
                head.rotation_quaternion = head_down
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + (1 + i) * OBJECT_APPEARANCE_TIME / 2
            )

            '''head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 1 * OBJECT_APPEARANCE_TIME
            )
            head.rotation_quaternion = head_back_right
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 2 * OBJECT_APPEARANCE_TIME
            )'''



        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

    def shake_no(
        self,
        start_time = None,
        end_time = None,
        attack = 0,
        decay = 0
    ):
        if start_time == None:
            raise Warning('Need start time for wince')

        if end_time == None:
            raise Warning('Need end time for wince')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        default_attack = OBJECT_APPEARANCE_TIME / 2

        if attack == None:
            if end_time == None:
                attack = default_attack / FRAME_RATE
            elif end_time - start_time > 2:
                attack = default_attack / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = default_attack / FRAME_RATE
            elif end_time - start_time > 2:
                decay = default_attack / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial = list(head.rotation_quaternion)

        head_left = [1, 0, 0.2, 0]
        head_right = [1, 0, -0.1, 0]

        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )

        #Shakes
        still_time = end_frame - start_frame - attack_frames - decay_frames
        num_shakes = math.floor(2 * still_time / OBJECT_APPEARANCE_TIME)
        for i in range(num_shakes):
            '''head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + still_time / 3
            )'''
            if i % 2 == 0:
                head.rotation_quaternion = head_left
            else:
                head.rotation_quaternion = head_right
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + (1 + i) * OBJECT_APPEARANCE_TIME / 2
            )

            '''head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 1 * OBJECT_APPEARANCE_TIME
            )
            head.rotation_quaternion = head_back_right
            head.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = start_frame + attack_frames + 2 * still_time / 3 + 2 * OBJECT_APPEARANCE_TIME
            )'''



        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame - decay_frames
        )
        head.rotation_quaternion = initial
        head.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = end_frame
        )

        '''#Eyes
        eyes = [
            self.ref_obj.children[0].children[-2],
            self.ref_obj.children[0].children[-3],
        ]
        for eye in eyes:
            init_eye_scale = list(eye.scale)
            init_eye_rot = list(eye.rotation_euler)

            eye.keyframe_insert(data_path = 'scale', frame = start_frame)
            eye.scale = [1, 0.3, 0.3]
            eye.keyframe_insert(data_path = 'scale', frame = start_frame + attack_frames)
            eye.keyframe_insert(data_path = 'scale', frame = end_frame - decay_frames)
            eye.scale = init_eye_scale
            eye.keyframe_insert(data_path = 'scale', frame = end_frame)

            eye.keyframe_insert(data_path = 'rotation_euler', frame = start_frame)
            if eye == eyes[1]:
                eye.rotation_euler = [0, -20 * math.pi / 180, 0]
            else:
                eye.rotation_euler = [0, 20 * math.pi / 180, 0]
            eye.keyframe_insert(data_path = 'rotation_euler', frame = start_frame + attack_frames)
            eye.keyframe_insert(data_path = 'rotation_euler', frame = end_frame - decay_frames)
            eye.rotation_euler = init_eye_rot
            eye.keyframe_insert(data_path = 'rotation_euler', frame = end_frame)'''

        '''leye = self.ref_obj.children[0].pose.bones[5]
        reye = self.ref_obj.children[0].pose.bones[6]

        for eye_bone in [leye, reye]:
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = start_frame)
            if eye_bone == leye:
                eye.rotation_quaternion = [1, 0, 0.1, 0]
            else:
                eye.rotation_quaternion = [1, 0, -0.1, 0]
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = start_frame + attack_frames)
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = end_frame - decay_frames)
            eye_bone.rotation_quaternion = init_eye_rot
            eye_bone.keyframe_insert(data_path = 'rotation_quaternion', frame = end_frame)'''

    def hold_object(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for hold_object')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE


        #Blob's left arm up = [1, -2.5, -8.1, -1.5]
        #Blob's right arm up = [1, 0.4, -36.6, -9]

        #These labels are from the point of view of the blob, which is opposite
        #from how they're labeled in the template .blend file. Huzzah.
        l_arm = None
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                l_arm = child.pose.bones[1]
                r_arm = child.pose.bones[2]

        #Left arm up
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = list(l_arm.rotation_quaternion)
        l_arm.rotation_quaternion = [1, 0.3, -0.2, -0.9]
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_frame != None:
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            l_arm.rotation_quaternion = initial_angle
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )

        #Right arm up
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        initial_angle = list(r_arm.rotation_quaternion)
        r_arm.rotation_quaternion = [0.837, 0.235, 0.215, 0.445]
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame + attack_frames
        )

        #And back
        if end_frame != None:
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame - decay_frames
            )
            r_arm.rotation_quaternion = initial_angle
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = end_frame
            )

    def show_mouth(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for hold_object')

        if end_time != None:
            raise Warning('End time not implemented for show_mouth')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        for child in self.ref_obj.children[0].children:
            if 'Mouth' in child.name:
                self.mouth = child
                break

        self.mouth.keyframe_insert(data_path = 'location', frame = start_frame)
        self.mouth.keyframe_insert(data_path = 'rotation_euler', frame = start_frame)
        self.mouth.keyframe_insert(data_path = 'scale', frame = start_frame)
        self.mouth.location = [-0.04, 0.36, 0.40609]
        self.mouth.rotation_euler = [
            -8.91 * math.pi / 180,
            -0.003 * math.pi / 180,
            -3.41 * math.pi / 180,
        ]
        self.mouth.scale = [
            0.487,
            0.719,
            0.398
        ]
        self.mouth.keyframe_insert(data_path = 'location', frame = start_frame + attack_frames)
        self.mouth.keyframe_insert(data_path = 'rotation_euler', frame = start_frame + attack_frames)
        self.mouth.keyframe_insert(data_path = 'scale', frame = start_frame + attack_frames)

    def hide_mouth(
        self,
        start_time = None,
        end_time = None,
        attack = None,
        decay = None
    ):
        if start_time == None:
            raise Warning('Need start time for hide_mouth')

        if end_time != None:
            raise Warning('End time not implemented for hide_mouth')

        start_frame = start_time * FRAME_RATE
        end_frame = None
        if end_time != None:
            end_frame = end_time * FRAME_RATE

        if attack == None:
            if end_time == None:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                attack = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                attack = (end_time - start_time) / 4
        attack_frames = attack * FRAME_RATE

        if decay == None:
            if end_time == None:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            elif end_time - start_time > 2:
                decay = OBJECT_APPEARANCE_TIME / FRAME_RATE
            else:
                decay = (end_time - start_time) / 4
        decay_frames = decay * FRAME_RATE

        for child in self.ref_obj.children[0].children:
            if 'Mouth' in child.name:
                self.mouth = child
                break

        self.mouth.keyframe_insert(data_path = 'scale', frame = start_frame)
        self.mouth.scale = [0, 0, 0]
        self.mouth.keyframe_insert(data_path = 'scale', frame = start_frame + attack_frames)

    def eat_animation(
        self,
        start_frame = None,
        end_frame = None,
        attack_frames = None,
        decay_frames = None
    ):
        if start_frame == None:
            raise Warning('Need start frame for eat animation')

        if attack_frames == None:
            if end_frame == None:
                attack_frames = OBJECT_APPEARANCE_TIME
            else:
                attack_frames = (end_frame - start_frame) / 2

        if decay_frames == None:
            if end_frame == None:
                decay_frames = OBJECT_APPEARANCE_TIME
            else:
                decay_frames = (end_frame - start_frame) / 2


        #I parented the mouth in a pretty ridiculous way, but it works.
        for child in self.ref_obj.children[0].children:
            if 'Mouth' in child.name or 'mouth' in child.name:
                mouth = child
                break

        new_action = bpy.data.actions.new('Mouth Open')
        if mouth.animation_data.action == None:
            mouth.animation_data_create()
        mouth.animation_data.action = new_action

        o_loc = list(mouth.location)
        o_rot = list(mouth.rotation_euler)
        o_scale = list(mouth.scale)

        mouth.keyframe_insert(data_path = 'location', frame = start_frame)
        mouth.keyframe_insert(data_path = 'rotation_euler', frame = start_frame)
        mouth.keyframe_insert(data_path = 'scale', frame = start_frame)

        mouth.location = [-0.04, 0.36, 0.3760]
        mouth.rotation_euler = [
            -8.91 * math.pi / 180,
            -0.003 * math.pi / 180,
            -3.41 * math.pi / 180,
        ]
        mouth.scale = [
            0.853,
            2.34,
            0.889
        ]

        if 'upright' in self.kwargs and self.kwargs['upright'] == True:
            mouth.location = [-0.04, -0.376, 1.29102]
            mouth.rotation_euler = [
                81.0898 * math.pi / 180,
                3.41 * math.pi / 180,
                -0.003005 * math.pi / 180,
            ]
            mouth.scale = [
                0.853,
                2.34,
                0.889
            ]

        mouth.keyframe_insert(data_path = 'location', frame = start_frame + attack_frames)
        mouth.keyframe_insert(data_path = 'rotation_euler', frame = start_frame + attack_frames)
        mouth.keyframe_insert(data_path = 'scale', frame = start_frame + attack_frames)

        mouth.keyframe_insert(data_path = 'location', frame = end_frame - decay_frames)
        mouth.keyframe_insert(data_path = 'rotation_euler', frame = end_frame - decay_frames)
        mouth.keyframe_insert(data_path = 'scale', frame = end_frame - decay_frames)

        mouth.location = o_loc
        mouth.rotation_euler = o_rot
        mouth.scale = o_scale

        mouth.keyframe_insert(data_path = 'location', frame = end_frame)
        mouth.keyframe_insert(data_path = 'rotation_euler', frame = end_frame)
        mouth.keyframe_insert(data_path = 'scale', frame = end_frame)

    def dance(
        self,
        start_time = None,
        end_time = None,
        beat_duration = 0.25,
        arms = True,
        neck = True
    ):
        if start_time == None:
            raise Warning('Need start time for dance')

        if end_time == None:
            raise Warning('Need end time for dance')

        start_frame = start_time * FRAME_RATE
        end_frame = end_time * FRAME_RATE

        #Head
        head = self.ref_obj.children[0].pose.bones[3]
        initial_head = list(head.location)
        head_left = [0, 0, -0.3]
        head_right = [0, 0, 0.3]


        l_arm = None
        r_arm = None
        for child in self.ref_obj.children:
            if 'blob' in child.name:
                l_arm = child.pose.bones[1]
                r_arm = child.pose.bones[2]

        initial_left = list(l_arm.rotation_quaternion)
        initial_right = list(r_arm.rotation_quaternion)


        l_arm_up_z = -2.7
        l_arm_down_z = 3
        l_arm_out_y = -7.6
        l_arm_forward_x = -3

        r_arm_up_z = -3.6
        r_arm_down_z = 1.8
        r_arm_out_y = -12.7
        r_arm_forward_x = -2.2

        head.keyframe_insert(
            data_path = "location",
            frame = start_frame
        )
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = start_frame
        )
        time = start_time
        i = 0
        while time < end_time:
            time += beat_duration
            i += 1 #Music starts on beat 1!
            if i % 2 == 1:
                head.location = head_left
                #l_arm.rotation_quaternion = initial_left
                l_arm.rotation_quaternion = [
                    1,
                    l_arm_forward_x,
                    l_arm_out_y,
                    l_arm_down_z
                ]
                r_arm.rotation_quaternion = [
                    1,
                    r_arm_forward_x,
                    r_arm_out_y,
                    r_arm_up_z
                ]
            else:
                head.location = head_right
                l_arm.rotation_quaternion = [
                    1,
                    l_arm_forward_x,
                    l_arm_out_y,
                    l_arm_up_z
                ]
                #r_arm.rotation_quaternion = initial_right
                r_arm.rotation_quaternion = [
                    1,
                    r_arm_forward_x,
                    r_arm_out_y,
                    r_arm_down_z
                ]

            head.keyframe_insert(
                data_path = "location",
                frame = time * FRAME_RATE
            )
            l_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = time * FRAME_RATE
            )
            r_arm.keyframe_insert(
                data_path = "rotation_quaternion",
                frame = time * FRAME_RATE
            )

        head.location = initial_head
        head.keyframe_insert(
            data_path = "location",
            frame = time * FRAME_RATE
        )
        l_arm.rotation_quaternion = initial_left
        l_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = time * FRAME_RATE
        )
        r_arm.rotation_quaternion = initial_right
        r_arm.keyframe_insert(
            data_path = "rotation_quaternion",
            frame = time * FRAME_RATE
        )

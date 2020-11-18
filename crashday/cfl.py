import struct

class CFL:
    def __init__(self):
        self.tile_name = ''
        self.model = ''
        self.size = '2 2'
        self.type = 'GROUND_FLAT'
        self.auto_list = 0
        self.substitution_model = 'NONE'
        self.maximum_random_bottom_shift = 0.0
        self.can_respawn = 1
        self.is_checkpoint = 0
        self.checkpoint_area = (0.0, 0.0, 0.0, 0.0)
        self.ai_free_roam = 1
        self.dynamics_drop_height = 'default'
        self.smoothing_lines = 'STOP'

    def write(self, file):
        file.write('Crashday-FieldObject-File\n')
        file.write(self.tile_name + '\n')
        file.write(self.model + '\n')
        file.write(self.size + '\n')
        file.write(self.type + '\n')
        file.write(str(self.auto_list) + '\n')
        file.write(self.substitution_model + '\n')
        file.write('{:.4g}'.format(self.maximum_random_bottom_shift) + '\n')
        file.write(str(self.can_respawn) + '\n')
        file.write(str(self.is_checkpoint) + '\n')
        if self.is_checkpoint:
            file.write('{:.4g} {:.4g} {:.4g} {:.4g}\n'.format(
                self.checkpoint_area[0], self.checkpoint_area[1], 
                self.checkpoint_area[2], self.checkpoint_area[3]))
        file.write(str(self.ai_free_roam) + '\n')
        file.write(self.dynamics_drop_height  + '\n')
        file.write(self.smoothing_lines  + '\n')
        file.write('\n-vegetation-\n\nNO_VEGETATION')
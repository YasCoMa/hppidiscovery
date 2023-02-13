import os
for g in os.listdir('../input_augmentation'):
    os.system('rm ../input_augmentation/'+g+'/da_step1.txt')
    os.system('rm ../input_augmentation/'+g+'/da_step2.txt')
    os.system('rm ../input_augmentation/'+g+'/da_step3.txt')

#!/usr/bin/env python3

import os
import struct
import sys

if __name__ == '__main__':
    ani_file_location = input("file location: ").strip('"')
    ani = ani_file_location

    stem = os.path.splitext(os.path.basename(ani_file_location))
    ani_file_location = stem[0] + '_edit' + stem[1]
    
    with open(ani, 'rb') as f:
        header = f.read(4)
        if header != b'ANI\0':
            input('Not an ani file. Press enter to exit')
            sys.exit()
        
        ani = header + f.read()
    
    anim_header_binary = ani[:8]
    event_count_binary = ani[8:12]
    event_count = struct.unpack('<I', event_count_binary)[0]
    
    offset = 12
    anim_events = []
    for _ in range(event_count):
        event_type_length = struct.unpack('<I', ani[offset:offset+4])[0]
        offset += 4
        
        event_type = ani[offset:offset+event_type_length]
        offset += event_type_length
        
        event_name_length = struct.unpack('<I', ani[offset:offset+4])[0]
        offset += 4
        
        event_name = ani[offset:offset+event_name_length]
        offset += event_name_length
        
        event_time = int(struct.unpack('<f', ani[offset:offset+4])[0])
        offset += 4
        
        anim_events.append((event_time, event_type.decode('utf-8'), event_name.decode('utf-8')))
    
    leftover_data = ani[offset:]
    
    while True:
        print()
        print('------- Events -------')
        for index, (time, type, name) in enumerate(anim_events):
            print(str(index) + ': ' + str(time) + ' | ' + type + ' | ' + name)
            
        print()
        user_input = input('Actions:\n> new [time (in ms), event type, event name]\n> remove [index]\n> insert/edit [index] [time (in ms), event type, event name]\n> exit/save (save the file)\n>>> ')
        if not any(user_input.lower().startswith(item) for item in ('new', 'remove', 'insert', 'edit', 'exit', 'save')):
            print('Not a valid option\n')
            continue
        
        if user_input.lower().startswith('new'):
            user_args = user_input.split(maxsplit=3)
            if not len(user_args) >= 4:
                print('Missing argument')
                continue
                
            _, time, event_type, event_name = user_args
            try:
                time = int(time)
            except ValueError:
                print('Time is not a number')
                continue
                
            anim_events.append((time, event_type, event_name))
        
        elif user_input.lower().startswith('remove'):
            user_args = user_input.split()
            if not len(user_args) >= 2:
                print('Missing argument')
                continue
            _, index = user_args
            try:
                index = int(index)
            except ValueError:
                print('Index is not a number')
                continue
            try:
                anim_events.pop(index)
            except IndexError:
                print('Out of range')
                continue
        
        elif user_input.lower().startswith('insert') or user_input.lower().startswith('edit'):
            user_args = user_input.split(maxsplit=4)
            if not len(user_args) >= 5:
                print('Missing argument')
                continue
                
            _, index, time, event_type, event_name = user_args
            try:
                index = int(index)
                time = int(time)
            except ValueError:
                print('Index or Time is not a number')
                continue
            
            try:
                anim_events[index] = (time, event_type, event_name)
            except IndexError:
                print('Out of range')
        
        elif user_input.lower().startswith('exit') or user_input.lower().startswith('save'):
            break
        
        anim_events = sorted(anim_events, key=lambda x: x[0])
    
    with open(ani_file_location, 'wb') as ani:
        ani.write(anim_header_binary)
        ani.write(struct.pack('<I', len(anim_events)))
        
        for time, event_type, event_name in anim_events:
            ani.write(struct.pack('<I', len(event_type)))
            ani.write(event_type.encode('utf-8'))
            ani.write(struct.pack('<I', len(event_name)))
            ani.write(event_name.encode('utf-8'))
            ani.write(struct.pack('<f', float(time)))
        ani.write(leftover_data)
    
    print()
    print('Saved file as: ' + ani_file_location)    
    input('Press enter to exit...')
    sys.exit()

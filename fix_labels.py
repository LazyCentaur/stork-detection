import os

# Función que busca y reemplaza el '1' por un '0' en los archivos .txt
def fix_labels_in_dir(directory):
    fixed_files_count = 0
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            lines = file.readlines()

        new_lines = []
        is_changed = False
        for line in lines:
            parts = line.strip().split()
            if parts and parts[0] == '1':
                parts[0] = '0'
                new_lines.append(" ".join(parts) + '\n')
                is_changed = True
            else:
                new_lines.append(line)

        if is_changed:
            with open(filepath, 'w') as file:
                file.writelines(new_lines)
            fixed_files_count += 1

    return fixed_files_count

# Rutas a las carpetas de etiquetas
train_labels_dir = 'dataset/labels/train'
val_labels_dir = 'dataset/labels/val'

print("Corrigiendo etiquetas en la carpeta de entrenamiento...")
count_train = fix_labels_in_dir(train_labels_dir)
print(f"Se modificaron {count_train} archivos en '{train_labels_dir}'")

print("\nCorrigiendo etiquetas en la carpeta de validación...")
count_val = fix_labels_in_dir(val_labels_dir)
print(f"Se modificaron {count_val} archivos en '{val_labels_dir}'")

print("\n¡Corrección completada!")
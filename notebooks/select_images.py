import os
import random
import shutil

# --- CONFIGURACIÓN ---
# Asegúrate de que estos nombres de carpeta son correctos.
source_images_dir = 'notebooks/data/raw_images'
source_labels_dir = 'notebooks/data/labels_yolo'
dataset_base_dir = 'dataset'
split_ratio = 0.8

print("--- INICIANDO SCRIPT DE ORGANIZACIÓN DE DATOS ---")
print(f"Directorio de imágenes de origen: '{source_images_dir}'")
print(f"Directorio de etiquetas de origen: '{source_labels_dir}'")
print("-" * 50)


# --- CREACIÓN DE CARPETAS ---
paths = {
    "train_images": os.path.join(dataset_base_dir, 'images', 'train'),
    "val_images": os.path.join(dataset_base_dir, 'images', 'val'),
    "train_labels": os.path.join(dataset_base_dir, 'labels', 'train'),
    "val_labels": os.path.join(dataset_base_dir, 'labels', 'val')
}
for path in paths.values():
    os.makedirs(path, exist_ok=True)

# --- PROCESO DE DIVISIÓN ---
# Verificamos si la carpeta de imágenes existe
if not os.path.isdir(source_images_dir):
    print(f"¡ERROR! La carpeta de imágenes '{source_images_dir}' no existe o no es un directorio.")
    all_images = []
else:
    all_images = [f for f in os.listdir(source_images_dir) if f.endswith('.jpg')]

print(f"Se encontraron {len(all_images)} imágenes .jpg en '{source_images_dir}'")

random.shuffle(all_images)
split_point = int(len(all_images) * split_ratio)
train_images = all_images[:split_point]
val_images = all_images[split_point:]

# Función para mover los archivos
def move_files(file_list, category):
    image_path_target = paths[f'{category}_images']
    label_path_target = paths[f'{category}_labels']
    
    for filename_jpg in file_list:
        base_filename = os.path.splitext(filename_jpg)[0]
        filename_txt = f"{base_filename}.txt"
        
        src_image = os.path.join(source_images_dir, filename_jpg)
        src_label = os.path.join(source_labels_dir, filename_txt)
        
        print(f"\n-> Procesando: {filename_jpg}")
        print(f"   Buscando etiqueta correspondiente en: {src_label}")
        
        if os.path.exists(src_label):
            print(f"   ¡Etiqueta encontrada! Moviendo archivos...")
            shutil.move(src_image, os.path.join(image_path_target, filename_jpg))
            shutil.move(src_label, os.path.join(label_path_target, filename_txt))
        else:
            print(f"   ¡ATENCIÓN! No se encontró la etiqueta para {filename_jpg}")

# Movemos los archivos
if len(all_images) > 0:
    print("-" * 50)
    print("Moviendo archivos de entrenamiento...")
    move_files(train_images, 'train')
    print("\nMoviendo archivos de validación...")
    move_files(val_images, 'val')
    print("-" * 50)

# --- RESULTADO FINAL ---
print("\n¡Proceso completado!")
# Volvemos a contar los archivos en las carpetas de destino para un resultado real
final_train_count = len(os.listdir(paths['train_images']))
final_val_count = len(os.listdir(paths['val_images']))

print(f"Archivos de entrenamiento: {final_train_count}")
print(f"Archivos de validación: {final_val_count}")
print(f"Estructura de carpetas creada en '{dataset_base_dir}'")
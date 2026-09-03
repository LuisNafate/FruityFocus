# 🥭 FruityFocus - Temporizador Pomodoro con Mascota Virtual de Escritorio

**FruityFocus** es una aplicación de escritorio nativa para Windows que transforma la técnica Pomodoro tradicional en una experiencia visual relajante e interactiva. En lugar de una ventana tradicional aburrida, un personaje animado en pixel art (un manguito con ojos expresivos) habita tu pantalla, descansando y caminando directamente sobre la barra de tareas de Windows.

---

## ✨ Características Principales

1. **Ventana Transparente con Click-Through**:
   - Fondo totalmente transparente (sin bordes ni marcos de ventana).
   - Máscara dinámica de colisión (`setMask`): solo el cuerpo del manguito detecta clics. Las áreas transparentes permiten hacer clic directamente sobre ventanas subyacentes e íconos de Windows sin estorbar.
   - Siempre visible en primer plano (*Always on Top*).

2. **Mascota Virtual Animada (5 Estados de Animación)**:
   - **Idle**: Mango respirando y parpadeando relajadamente.
   - **Walk Cycle**: Camina de lado a lado sobre la barra de tareas e invierte su dirección al llegar a los bordes.
   - **Focus Mode**: Rostro decidido con gota de sudor animada mientras trabajas.
   - **Break Mode**: Mango descansando plácidamente con animación de 'z Z Z' flotante.
   - **Celebration**: Salta de alegría con las manos en alto y confeti parpadeante al finalizar una sesión de concentración.

3. **Físicas de Gravedad y Drag & Drop**:
   - Haz clic y arrastra al mango a cualquier lugar de la pantalla.
   - Al soltarlo en el aire, caerá hacia abajo con gravedad simulada y un rebote amortiguado realista al posarse de vuelta sobre la barra de tareas.

4. **Bocadillo de Diálogo / HUD Flotante (Speech Bubble)**:
   - Muestra el tiempo restante en formato retro digital (`MM:SS`).
   - Botones rápidos para Iniciar/Pausar (`▶`/`⏸`), Reiniciar (`🔄`), Saltar período (`⏭`) y Configuración (`⚙`).
   - Puedes ocultarlo o mostrarlo haciendo un clic rápido sobre el mango.

5. **Menú Contextual Nativo (Clic Derecho)**:
   - Control total del temporizador (Iniciar, Pausar, Reiniciar, Saltar).
   - Ajustar el tamaño del personaje: Pequeño (64px), Normal (96px) o Grande (128px).
   - Diálogo de configuración para personalizar los minutos de concentración y descanso.
   - Salir de la aplicación limpiamente.

6. **Integración con la Bandeja del Sistema (System Tray)**:
   - Ícono con forma de manguito en la bandeja del sistema de Windows con menú de acceso rápido.

---

## 🚀 Cómo Ejecutar

### Requisitos Previos:
- Python 3.10 o superior (probado en Python 3.13)
- Dependencias instaladas:
  ```powershell
  pip install -r requirements.txt
  ```

### Ejecutar la Aplicación:
```powershell
python main.py
```

---

## 🛠️ Empaquetado a Ejecutable (.exe)

Para compilar FruityFocus en un ejecutable independiente de Windows sin consola de depuración:
```powershell
python build.py
```
El ejecutable resultante se encontrará en la carpeta `dist/FruityFocus/FruityFocus.exe`.

---

## 🎮 Controles Rápidos

- **Clic Izquierdo + Arrastrar**: Mover al mango por la pantalla. Al soltarlo, cae por gravedad.
- **Clic Izquierdo Rápido (sin arrastrar)**: Muestra u oculta el bocadillo con el contador.
- **Clic Derecho**: Despliega el menú contextual de configuración y controles.

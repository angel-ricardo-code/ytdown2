# GUÍA DE ESPECIFICACIONES VISUALES
# YoutubeFake Downloader — Preview 5 (Minimalista con Pausa/Resumir)
# Formato: Especificación técnica para implementación en PySide6
# ============================================================================

==============================================================================
1. PALETA DE COLORES
==============================================================================

Nombre                    Hex        Uso
-------------------------- ---------- ----------------------------------------
AZUL_PRIMARIO             #0071e3    Botón principal, acentos, barra progreso
AZUL_PRIMARIO_HOVER       #0051a2    Hover del botón principal
AZUL_SECUNDARIO           #42a5f5    Gradiente de la barra de progreso
GRIS_FONDO                #f5f5f7    Fondo de la ventana, fondo de campos
GRIS_BORDE                #d2d2d7    Bordes, separadores
GRIS_TEXTO                #86868b    Labels, texto secundario, placeholders
NEGRO_TEXTO               #1d1d1f    Títulos, texto principal
BLANCO                    #ffffff    Fondo de la ventana, fondo de inputs focus
ROJO_CANCELAR             #ff3b30    Botón cancelar, botón cancelar pequeño
ROJO_CANCELAR_HOVER       #d32f2f    Hover del botón cancelar
AMARILLO_PAUSA            #b45309    Texto del botón pausa (sobre fondo crema)
AMARILLO_PAUSA_FONDO      #fff3cd    Fondo del botón pausa
VERDE_RESUMIR             #15803d    Texto del botón resumir (sobre fondo verde)
VERDE_RESUMIR_FONDO       #dcfce7    Fondo del botón resumir
ROJO_CANCELAR_SM_FONDO    #fee2e2    Fondo del botón cancelar pequeño
NEGRO_LOG                 #1d1d1f    Fondo del área de registro
GRIS_LOG_TEXTO            #a1a1a6    Texto general del log
GRIS_LOG_TIEMPO           #6e6e73    Timestamps del log
AZUL_LOG_INFO             #5ac8fa    Líneas de información en el log
VERDE_LOG_OK              #34c759    Líneas de éxito en el log
AMARILLO_LOG_WARN         #ff9f0a    Líneas de advertencia/pausa en el log
GRIS_TOOLBAR              #f5f5f7    Fondo superior de la barra de herramientas
GRIS_TOOLBAR_BORDE        #e8e8ed    Degradado inferior de la toolbar
GRIS_PROGRESS_BG          #e8e8ed    Fondo de la barra de progreso (vacía)

==============================================================================
2. TIPOGRAFÍA
==============================================================================

Familia:        -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
                (En PySide6 usar QFont("Segoe UI") o QFont("SF Pro") en macOS)

Elemento        Tamaño      Peso        Color           Notas
--------------- ----------- ----------- --------------- ------------------------
Título ventana  13px        600         #1d1d1f         Barra de título
H1 (hero)       19px        700         #1d1d1f         Título principal
Subtítulo       12px        400         #86868b         Bajo el H1
Label campo     11px        600         #86868b         Mayúsculas, letter-spacing 0.5px
Input texto     13px        400         #1d1d1f         Placeholder: #86868b
Botón small     12px        600         #0071e3         Examinar...
Botón control   12px        700         variable        Según estado (pausa/resume/cancel)
Botón primary   14px        700         #ffffff         Descargar
Botón secondary 13px        600         #ff3b30         Cancelar descarga
Progreso título 13px        700         #1d1d1f         "Descargando video"
Progreso %      15px        800         #0071e3         "67%"
Meta texto      11px        400         #86868b         Labels de velocidad/eta/tamaño
Meta valor      11px        600         #1d1d1f         Números dentro de meta
Log texto       10px        400         #a1a1a6         Texto general del log
Log timestamp   10px        400         #6e6e73         Horas en el log

==============================================================================
3. DIMENSIONES Y ESPACIADO
==============================================================================

VENTANA PRINCIPAL
  - Ancho:              520px  (fijo)
  - Alto mínimo:        600px  (ajustable según contenido)
  - Radio de esquinas:  18px
  - Sombra:             0px 32px 64px rgba(0,0,0,0.12)

TOOLBAR (Barra de título tipo macOS)
  - Altura:             44px
  - Padding:            12px 20px
  - Fondo:              degradado vertical #f5f5f7 → #e8e8ed
  - Borde inferior:     1px sólido #d2d2d7
  - Semáforos:          3 círculos de 12px, gap 10px entre ellos
    · Cerrar:   #ff5f57
    · Minimizar:#febc2e
    · Maximizar:#28c840
  - Título:             6px a la derecha del último semáforo

CONTENIDO (Área debajo de la toolbar)
  - Padding:            24px 28px 28px 28px
  - Gap entre secciones:14px (margin-bottom de cada field)

HERO (Icono + título + subtítulo)
  - Margin-bottom:      22px
  - Icono contenedor:   56px × 56px, radio 16px
  - Icono SVG:          28px × 28px, centrado
  - Sombra del icono:   0px 6px 20px rgba(0,113,227,0.2)
  - H1 margin-top:      12px debajo del icono
  - Subtítulo margin:   3px debajo del H1

CAMPOS DE ENTRADA (Field)
  - Margin-bottom:      14px entre campos
  - Label margin-bottom:6px debajo del label
  - Input:
    · Altura interna:   44px (padding 11px 14px)
    · Radio:            10px
    · Fondo normal:     #f5f5f7
    · Foco:             fondo #ffffff, borde 1px #0071e3, shadow 0 0 0 4px rgba(0,113,227,0.1)
    · Transición:       0.2s en todos los cambios

FILA CON BOTÓN (URL + Examinar, etc.)
  - Layout:             flex horizontal
  - Gap:                10px entre input y botón
  - Input:              flex: 1 (ocupa todo el espacio restante)

BOTÓN SMALL (Examinar...)
  - Padding:            10px 16px
  - Radio:              10px
  - Fondo:              #f5f5f7
  - Borde:              1px #d2d2d7
  - Texto:              #0071e3, 12px, weight 600
  - Hover:              fondo #e8e8ed
  - Icono SVG:          14px × 14px, a la izquierda del texto, gap 6px

SELECT (Combo de calidad)
  - Mismas dimensiones que input
  - Flecha desplegable: SVG custom 12px, color #86868b, posicionada a 12px del borde derecho
  - Padding-right:      32px (para dejar espacio a la flecha)
  - Opciones con emoji: incluir icono al inicio del texto de cada option

SECCIÓN DE PROGRESO (Card)
  - Fondo:              #f5f5f7
  - Radio:              14px
  - Padding:            18px
  - Margin:             18px 0 (arriba y abajo)

  CABECERA DEL PROGRESO
    · Layout:           flex, justify-content: space-between, align-items: center
    · Margin-bottom:    12px
    · Título:           icono 15px + gap 6px + texto
    · Porcentaje:       15px, weight 800, color #0071e3

  BARRA DE PROGRESO
    · Track (fondo):    #e8e8ed, altura 8px, radio 8px
    · Fill (progreso):  degradado 90deg #0071e3 → #42a5f5, misma altura y radio
    · Transición:       width 0.3s ease

  METADATOS (Velocidad / ETA / Tamaño)
    · Layout:           flex, gap 16px, margin-top 14px
    · Cada item:        flex 1, icono 14px + gap 8px + texto
    · Texto label:      11px, #86868b
    · Texto valor:      11px, #1d1d1f, weight 600

  BARRA DE CONTROL (Pausa / Resumir / Cancelar)
    · Layout:           flex, gap 10px, margin-top 14px
    · Cada botón:       flex 1 (mismo ancho), padding 10px, radio 10px
    · Icono SVG:        16px × 16px, a la izquierda del texto, gap 8px
    · Tipografía:       12px, weight 700

    BOTÓN PAUSA:
      · Fondo:          #fff3cd
      · Texto:          #b45309
      · Hover:          #fef3c7
      · Icono:          dos rectángulos verticales (pause)

    BOTÓN RESUMIR:
      · Fondo:          #dcfce7
      · Texto:          #15803d
      · Hover:          #d1fae5
      · Icono:          triángulo apuntando derecha (play)
      · Estado:         visible solo cuando está pausado (alternar con Pausa)

    BOTÓN CANCELAR PEQUEÑO:
      · Fondo:          #fee2e2
      · Texto:          #dc2626
      · Hover:          #fecaca
      · Icono:          X (dos líneas cruzadas)

ÁREA DE LOG (Registro)
  - Margin-top:         6px (desde el label)
  - Fondo:              #1d1d1f
  - Radio:              14px
  - Padding:            14px 16px
  - Altura:             110px
  - Overflow:           auto (scroll vertical si excede)
  - Fuente:             'SF Mono', 'Consolas', monospace, 10px
  - Line-height:        1.8
  - Color base:         #a1a1a6

  LÍNEA DE LOG:
    · Layout:           flex, gap 8px, align-items: flex-start
    · Timestamp:        42px ancho fijo, color #6e6e73, no-wrap
    · Icono inline:     11px, antes del mensaje
    · Colores según tipo:
      - Info:   #5ac8fa
      - OK:     #34c759
      - Warn:   #ff9f0a
      - Normal: #a1a1a6

BOTÓN PRINCIPAL (Descargar)
  - Width:              100%
  - Padding:            14px
  - Radio:              12px
  - Fondo:              degradado 135deg #0071e3 → #42a5f5
  - Texto:              #ffffff, 14px, weight 700
  - Sombra:             0px 4px 16px rgba(0,113,227,0.25)
  - Margin-top:         16px
  - Hover:
    · Transform:        translateY(-1px)
    · Sombra:           0px 6px 20px rgba(0,113,227,0.35)
  - Icono SVG:          18px × 18px, a la izquierda del texto, gap 8px

BOTÓN SECONDARY (Cancelar descarga)
  - Width:              100%
  - Padding:            12px
  - Radio:              12px
  - Fondo:              transparente
  - Borde:              1.5px #ff3b30
  - Texto:              #ff3b30, 13px, weight 600
  - Margin-top:         10px
  - Hover:
    · Fondo:            #ff3b30
    · Texto:            #ffffff
  - Icono SVG:          15px × 15px, a la izquierda del texto, gap 6px

==============================================================================
4. ICONOS SVG (Especificación de paths)
==============================================================================

Todos los iconos son SVG vectoriales de 24×24 viewBox, stroke-based.
En PySide6 se pueden cargar como QIcon desde archivos .svg o como
QPixmap renderizado desde strings SVG.

ICONO_DESCARGA (Botón principal, hero)
  <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>

ICONO_CARPETA (Botón Examinar)
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
  </svg>

ICONO_PAUSA (Botón Pausar)
  <svg viewBox="0 0 24 24" fill="currentColor">
    <rect x="6" y="4" width="4" height="16" rx="1"/>
    <rect x="14" y="4" width="4" height="16" rx="1"/>
  </svg>
  NOTA: fill="currentColor" para heredar el color del texto (#b45309)

ICONO_PLAY (Botón Resumir)
  <svg viewBox="0 0 24 24" fill="currentColor">
    <polygon points="5 3 19 12 5 21 5 3"/>
  </svg>
  NOTA: fill="currentColor" para heredar el color del texto (#15803d)

ICONO_X (Botón Cancelar pequeño, botón Cancelar grande)
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>

ICONO_ENLACE (Label URL)
  Emoji: 🔗  o  SVG de cadena (opcional)

ICONO_CALIDAD (Label Calidad)
  Emoji: 🎬  o  SVG de película (opcional)

ICONO_REGISTRO (Label Log)
  Emoji: 📝  o  SVG de documento (opcional)

ICONO_VELOCIDAD (Meta)
  Emoji: ⚡

ICONO_RELOJ (Meta)
  Emoji: ⏱️

ICONO_DISCO (Meta)
  Emoji: 💾

ICONO_PLAY_ESTADO (Título progreso)
  Emoji: ▶️

==============================================================================
5. COMPORTAMIENTOS Y ESTADOS
==============================================================================

ESTADO INICIAL (Antes de iniciar descarga)
  - Barra de progreso:  0%, track vacío
  - Botón Descargar:    visible, habilitado
  - Botón Cancelar:     visible, habilitado
  - Barra de control:   OCULTA (pausa/resume/cancelar pequeño no se muestran)
  - Log:                vacío o con mensaje "Listo. Esperando URL..."
  - Meta datos:         ocultos o mostrando guiones

ESTADO DESCARGANDO
  - Barra de progreso:  animándose según porcentaje real
  - Botón Descargar:    OCULTO o deshabilitado
  - Botón Cancelar:     OCULTO
  - Barra de control:   VISIBLE
    · Pausa:            visible y habilitado
    · Resumir:          OCULTO
    · Cancelar pequeño: visible y habilitado
  - Log:                actualizándose en tiempo real
  - Meta datos:         visibles con valores reales

ESTADO PAUSADO
  - Barra de progreso:  congelada en el último porcentaje
  - Botón Pausa:        OCULTO
  - Botón Resumir:      VISIBLE y habilitado
  - Log:                nueva línea "⏸️ Descarga pausada por usuario"
  - Meta datos:         congelados, ETA muestra "Pausado"

ESTADO RESUMIENDO
  - Botón Resumir:      OCULTO
  - Botón Pausa:        VISIBLE
  - Log:                nueva línea "▶️ Reanudando descarga..."
  - Progreso:           continúa desde donde se pausó

ESTADO COMPLETADO
  - Barra de progreso:  100%
  - Barra de control:   OCULTA
  - Botón Descargar:    VISIBLE (texto cambiado a "Descargar otro")
  - Log:                línea final "✅ Descarga completada: [ruta]"
  - Diálogo:            QMessageBox.information con ruta del archivo

ESTADO CANCELADO / ERROR
  - Barra de control:   OCULTA
  - Botón Descargar:    VISIBLE y habilitado
  - Log:                línea de error o cancelación
  - Barra de progreso:  opcionalmente se resetea a 0 o se mantiene congelada

==============================================================================
6. IMPLEMENTACIÓN EN PYSIDE6 — CHECKLIST DE COMPONENTES
==============================================================================

[ ] QMainWindow o QWidget como contenedor principal
    · setWindowFlags(Qt.FramelessWindowHint)  <- para borde custom tipo macOS
    · setAttribute(Qt.WA_TranslucentBackground)  <- si se quiere sombra nativa
    · setFixedWidth(520)

[ ] QWidget personalizado para la toolbar
    · Altura fija 44px
    · Tres QLabels circulares (semáforos) o botones reales
    · QLabel con el título
    · mousePressEvent / mouseMoveEvent para drag de ventana

[ ] QVBoxLayout como layout principal del contenido
    · setContentsMargins(28, 24, 28, 28)
    · setSpacing(14)

[ ] Sección HERO
    · QWidget contenedor, centrado
    · QLabel con QPixmap del icono SVG renderizado
    · QLabel para H1 (font: 19px, weight 700)
    · QLabel para subtítulo (font: 12px, color #86868b)

[ ] Campos de entrada (reutilizar un método/función)
    · QLabel para el label (font: 11px, uppercase, color #86868b)
    · QLineEdit para input
      - setStyleSheet con fondo #f5f5f7, radio 10px, padding
      - focusPolicy y señal textChanged si se quiere validación
    · QPushButton para "Examinar..." (con icono SVG cargado vía QIcon)
    · QFileDialog::getExistingDirectory() al hacer clic

[ ] QComboBox para calidad
    · addItem("⭐ Best (mejor disponible)")
    · addItem("🖥️ 1080p Full HD")
    · etc.
    · setStyleSheet para quitar estilo nativo y aplicar custom

[ ] Sección de progreso (QWidget contenedor)
    · setStyleSheet("background: #f5f5f7; border-radius: 14px;")
    · QHBoxLayout para cabecera (título + porcentaje)
    · QProgressBar para la barra
      - setTextVisible(False)  <- el porcentaje se muestra en un QLabel aparte
      - setStyleSheet con track #e8e8ed y chunk degradado
    · QHBoxLayout para metadatos (3 QLabel con icono + texto)
    · QHBoxLayout para barra de control (3 QPushButton)

[ ] Barra de control (3 botones)
    · QPushButton btnPause
      - setVisible(True/False) según estado
      - clicked.connect(self._pause_download)
    · QPushButton btnResume
      - setVisible(False) por defecto
      - clicked.connect(self._resume_download)
    · QPushButton btnCancelSmall
      - clicked.connect(self._cancel_download)

[ ] Área de log (QTextEdit o QListWidget)
    · setReadOnly(True)
    · setStyleSheet con fondo #1d1d1f, fuente monospace
    · append() para agregar líneas con HTML opcional para colores
    · Alternativa: usar QListWidget con items formateados para mejor rendimiento

[ ] Botón principal (QPushButton)
    · setStyleSheet con degradado, sombra, hover translateY
    · QPropertyAnimation opcional para efecto de pulso al completar

[ ] Botón secondary (QPushButton)
    · setStyleSheet con borde #ff3b30, hover con fondo sólido

[ ] QThread / QObject + moveToThread para el worker
    · NO usar QThread directamente si se necesita pausa/resume complejo
    · Mejor: threading.Thread de Python con un threading.Event() para pausa
    · Comunicación: señales pyqtSignal desde el worker hacia la UI

[ ] Señales necesarias (pyqtSignal):
    · progress_signal = Signal(int)           -> porcentaje 0-100
    · speed_signal = Signal(str)              -> "2.4 MB/s"
    · eta_signal = Signal(str)                -> "1m 23s"
    · size_signal = Signal(str)               -> "156 MB"
    · log_signal = Signal(str, str)           -> (tipo, mensaje) ej: ("info", "texto")
    · finished_signal = Signal(str)           -> ruta final
    · error_signal = Signal(str)              -> mensaje de error
    · paused_signal = Signal()                -> notificar que se pausó
    · resumed_signal = Signal()               -> notificar que se reanudó

[ ] Mecanismo de pausa en el worker:
    · threading.Event() llamado 'pause_event'
    · En el bucle de descarga, verificar:
        if not self.pause_event.is_set():
            self.pause_event.wait()  # <- bloquea hasta que se llame .set()
    · Métodos expuestos:
        def pause(self): self.pause_event.clear()
        def resume(self): self.pause_event.set()

==============================================================================
7. EJEMPLO DE STYLE SHEET GLOBAL (Referencia)
==============================================================================

Este es un fragmento orientativo. En PySide6 se aplica con
app.setStyleSheet(global_stylesheet) o widget por widget.

QWidget {
    font-family: "Segoe UI", sans-serif;
}

QLineEdit, QComboBox {
    background: #f5f5f7;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 11px 14px;
    font-size: 13px;
    color: #1d1d1f;
}
QLineEdit:focus, QComboBox:focus {
    background: #ffffff;
    border-color: #0071e3;
}

QProgressBar {
    background: #e8e8ed;
    border: none;
    border-radius: 8px;
    height: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0071e3, stop:1 #42a5f5);
    border-radius: 8px;
}

QPushButton#btnPrimary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0071e3, stop:1 #42a5f5);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#btnPrimary:hover {
    background: #0051a2;
}

QTextEdit#logArea {
    background: #1d1d1f;
    color: #a1a1a6;
    border: none;
    border-radius: 14px;
    padding: 14px 16px;
    font-family: "Consolas", monospace;
    font-size: 10px;
}

==============================================================================
8. NOTAS FINALES
==============================================================================

- Los emojis pueden no renderizar igual en todos los sistemas Windows.
  Para máxima compatibilidad, reemplazar por SVGs o usar la fuente
  "Segoe UI Emoji" explícitamente.

- El borde redondeado de la ventana completa en Windows requiere
  setWindowFlags(Qt.FramelessWindowHint) + implementar manualmente
  el resize y el drag. Alternativa: mantener borde nativo de Windows
  y solo aplicar el diseño al contenido interno.

- Para que la barra de progreso se actualice sin saltos, usar
  QPropertyAnimation sobre el valor o actualizar con setValue()
  directamente desde la señal del worker.

- El log con colores se puede lograr insertando HTML en QTextEdit:
  self.txt_log.append(f'<span style="color:#5ac8fa">{timestamp}</span> {msg}')

- Para la pausa real de la descarga, el core debe soportar chunked
  downloads donde entre chunk y chunk se verifique el Event.
  Si el core usa una librería externa (requests, httpx), puede ser
  necesario envolver la iteración de chunks con la verificación.

==============================================================================
FIN DEL DOCUMENTO
==============================================================================

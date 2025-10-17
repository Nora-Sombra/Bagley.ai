import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import threading
import speech_recognition as sr
import pyttsx3

class BagleyGUI:
    
    def __init__(self):
        # Configurar Gemini
        api_key = "AIzaSyAVVZ-fUa3bYoNqFAXXseEYNg7oO1OO4_w" 
        genai.configure(api_key=api_key)
        
        self.historial = []
        self.modo_actual = "psicologo"
        
        # Configurar voz (Text-to-Speech)
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Velocidad de habla
        self.engine.setProperty('volume', 0.9)  # Volumen
        
        # Configurar voces en español si están disponibles
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'spanish' in voice.languages or 'es' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Configurar reconocimiento de voz
        self.recognizer = sr.Recognizer()
        self.esta_hablando = False
        self.voz_activada = True
        
        # Prompts para cada modo
        self.prompts = {
            "psicologo": """Eres Bagley, un consejero emocional empático, comprensivo y amable.
Ayudas a las personas con sus problemas personales y familiares.
Muestra empatía, valida sentimientos y ofrece perspectivas constructivas.
Responde de manera cálida y comprensiva. Máximo 150 palabras (porque se leerá en voz alta).""",
            
            "deberes": """Eres Bagley, un tutor educativo paciente y claro.
Ayudas con deberes escolares de cualquier materia: matemáticas, ciencias, historia, lengua, etc.
Explica paso a paso, usa ejemplos y asegúrate de que el estudiante entienda.
Sé motivador y haz que aprender sea divertido. Máximo 150 palabras.""",
            
            "programacion": """Eres Bagley, un mentor de programación experto y amigable.
Ayudas con código, errores, conceptos de programación y proyectos.
Explica de forma clara, proporciona ejemplos de código cuando sea necesario.
Eres paciente y animas a seguir aprendiendo. Máximo 150 palabras."""
        }
        
        # Crear ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Bagley - Tu Asistente Personal 💙")
        self.ventana.state('zoomed')
        
        # Obtener dimensiones de la pantalla
        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        
        # Intentar cargar imagen de fondo
        try:
            self.imagen_fondo = Image.open("Blume_Bagley.png")
            self.imagen_fondo = self.imagen_fondo.resize((ancho_pantalla, alto_pantalla), Image.Resampling.LANCZOS)
            self.foto_fondo = ImageTk.PhotoImage(self.imagen_fondo)
            
            self.canvas = tk.Canvas(self.ventana, width=ancho_pantalla, height=alto_pantalla)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.foto_fondo, anchor="nw")
        except:
            self.canvas = tk.Canvas(self.ventana, width=ancho_pantalla, height=alto_pantalla, bg="#1a1a2e")
            self.canvas.pack(fill="both", expand=True)
            print("⚠️  No se encontró 'Blume_Bagley.png'. Usando fondo de color.")
        
        self.crear_interfaz()
    
    def hablar(self, texto):
        """Hace que Bagley hable el texto"""
        if self.voz_activada and not self.esta_hablando:
            def _hablar():
                self.esta_hablando = True
                try:
                    self.engine.say(texto)
                    self.engine.runAndWait()
                except:
                    pass
                finally:
                    self.esta_hablando = False
            
            threading.Thread(target=_hablar, daemon=True).start()
    
    def escuchar_microfono(self):
        """Escucha por micrófono y convierte voz a texto"""
        def _escuchar():
            try:
                # Cambiar estado del botón
                self.ventana.after(0, lambda: self.boton_mic.config(
                    text="🎤 Escuchando...", 
                    bg="#e74c3c"
                ))
                
                with sr.Microphone() as source:
                    # Ajustar al ruido ambiente
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Escuchar
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # Convertir a texto
                    texto = self.recognizer.recognize_google(audio, language="es-ES")
                    
                    # Mostrar en la entrada y enviar
                    self.ventana.after(0, lambda: self.entrada_texto.delete(0, tk.END))
                    self.ventana.after(0, lambda: self.entrada_texto.insert(0, texto))
                    self.ventana.after(0, self.enviar_mensaje)
                    
            except sr.WaitTimeoutError:
                self.ventana.after(0, lambda: messagebox.showinfo(
                    "Tiempo agotado",
                    "No escuché nada. Intenta de nuevo."
                ))
            except sr.UnknownValueError:
                self.ventana.after(0, lambda: messagebox.showinfo(
                    "No entendí",
                    "No pude entender lo que dijiste. ¿Puedes repetirlo?"
                ))
            except sr.RequestError:
                self.ventana.after(0, lambda: messagebox.showerror(
                    "Error",
                    "No hay conexión a internet para el reconocimiento de voz."
                ))
            except Exception as e:
                self.ventana.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Error al escuchar: {str(e)}"
                ))
            finally:
                # Restaurar botón
                self.ventana.after(0, lambda: self.boton_mic.config(
                    text="🎤 Hablar",
                    bg="#2ecc71"
                ))
        
        threading.Thread(target=_escuchar, daemon=True).start()
    
    def toggle_voz(self):
        """Activa/desactiva la voz de Bagley"""
        self.voz_activada = not self.voz_activada
        
        if self.voz_activada:
            self.boton_voz.config(text="🔊 Voz ON", bg="#27ae60")
        else:
            self.boton_voz.config(text="🔇 Voz OFF", bg="#95a5a6")
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Frame principal con fondo semitransparente
        frame_principal = tk.Frame(self.canvas, bg="#f0f0f0", bd=0)
        frame_principal.place(relx=0.5, rely=0.5, anchor="center", width=900, height=650)
        
        # Frame superior con título y selector de modo
        frame_superior = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_superior.pack(pady=15, fill=tk.X, padx=20)
        
        # Título
        titulo = tk.Label(
            frame_superior,
            text="💙 Bagley - Tu Asistente Personal",
            font=("Arial", 22, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        titulo.pack(side=tk.LEFT)
        
        # Frame de botones de modo
        frame_modos = tk.Frame(frame_superior, bg="#f0f0f0")
        frame_modos.pack(side=tk.RIGHT)
        
        # Botones de modo
        self.btn_psicologo = tk.Button(
            frame_modos,
            text="💙 Psicólogo",
            command=lambda: self.cambiar_modo("psicologo"),
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.btn_psicologo.pack(side=tk.LEFT, padx=5)
        
        self.btn_deberes = tk.Button(
            frame_modos,
            text="📚 Deberes",
            command=lambda: self.cambiar_modo("deberes"),
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.btn_deberes.pack(side=tk.LEFT, padx=5)
        
        self.btn_programacion = tk.Button(
            frame_modos,
            text="💻 Programación",
            command=lambda: self.cambiar_modo("programacion"),
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.btn_programacion.pack(side=tk.LEFT, padx=5)
        
        # Indicador de modo actual
        self.label_modo = tk.Label(
            frame_principal,
            text="Modo: Psicólogo 💙",
            font=("Arial", 12, "italic"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.label_modo.pack(pady=5)
        
        # Área de chat con bordes
        frame_chat = tk.Frame(frame_principal, bg="#ffffff", bd=2, relief=tk.SOLID)
        frame_chat.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.area_chat = scrolledtext.ScrolledText(
            frame_chat,
            wrap=tk.WORD,
            width=100,
            height=20,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#2c3e50",
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.area_chat.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada
        frame_entrada = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_entrada.pack(pady=15, padx=20, fill=tk.X)
        
        # Botón de micrófono
        self.boton_mic = tk.Button(
            frame_entrada,
            text="🎤 Hablar",
            command=self.escuchar_microfono,
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.boton_mic.pack(side=tk.LEFT, padx=(0, 10))
        
        # Campo de texto
        self.entrada_texto = tk.Entry(
            frame_entrada,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#2c3e50",
            relief=tk.SOLID,
            bd=2
        )
        self.entrada_texto.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.entrada_texto.bind("<Return>", lambda e: self.enviar_mensaje())
        
        # Botón enviar
        self.boton_enviar = tk.Button(
            frame_entrada,
            text="Enviar 💬",
            command=self.enviar_mensaje,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor="hand2"
        )
        self.boton_enviar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón toggle voz
        self.boton_voz = tk.Button(
            frame_entrada,
            text="🔊 Voz ON",
            command=self.toggle_voz,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.boton_voz.pack(side=tk.LEFT)
        
        # Mensaje de bienvenida
        mensaje_bienvenida = (
            "¡Hola! Soy Bagley, tu asistente personal 💙\n\n"
            "Puedo ayudarte con:\n"
            "💙 Apoyo emocional y problemas personales\n"
            "📚 Deberes y tareas escolares\n"
            "💻 Programación y código\n\n"
            "🎤 Puedes HABLARME presionando el botón verde\n"
            "⌨️ O escribirme en el cuadro de texto\n\n"
            "Actualmente estoy en modo: Psicólogo\n"
            "¿En qué puedo ayudarte hoy?"
        )
        self.mostrar_mensaje("Bagley", mensaje_bienvenida, "#3498db")
        self.hablar("¡Hola! Soy Bagley. Puedo ayudarte como psicólogo, con deberes o con programación. ¿En qué puedo ayudarte?")
    
    def cambiar_modo(self, nuevo_modo):
        """Cambia el modo de operación de Bagley"""
        self.modo_actual = nuevo_modo
        
        # Actualizar estilos de botones
        self.btn_psicologo.config(
            bg="#3498db" if nuevo_modo == "psicologo" else "#ecf0f1",
            fg="white" if nuevo_modo == "psicologo" else "#2c3e50",
            font=("Arial", 10, "bold" if nuevo_modo == "psicologo" else "normal")
        )
        self.btn_deberes.config(
            bg="#e67e22" if nuevo_modo == "deberes" else "#ecf0f1",
            fg="white" if nuevo_modo == "deberes" else "#2c3e50",
            font=("Arial", 10, "bold" if nuevo_modo == "deberes" else "normal")
        )
        self.btn_programacion.config(
            bg="#9b59b6" if nuevo_modo == "programacion" else "#ecf0f1",
            fg="white" if nuevo_modo == "programacion" else "#2c3e50",
            font=("Arial", 10, "bold" if nuevo_modo == "programacion" else "normal")
        )
        
        # Actualizar label de modo
        modos_texto = {
            "psicologo": "Modo: Psicólogo 💙",
            "deberes": "Modo: Deberes 📚",
            "programacion": "Modo: Programación 💻"
        }
        self.label_modo.config(text=modos_texto[nuevo_modo])
        
        # Mensaje de cambio
        mensajes_cambio = {
            "psicologo": "Ahora estoy en modo Psicólogo. Cuéntame qué te preocupa 💙",
            "deberes": "Ahora estoy en modo Deberes. ¿Con qué materia necesitas ayuda? 📚",
            "programacion": "Ahora estoy en modo Programación. ¿Qué código quieres crear o arreglar? 💻"
        }
        
        colores = {
            "psicologo": "#3498db",
            "deberes": "#e67e22",
            "programacion": "#9b59b6"
        }
        
        self.mostrar_mensaje("Bagley", mensajes_cambio[nuevo_modo], colores[nuevo_modo])
        self.hablar(mensajes_cambio[nuevo_modo])
    
    def mostrar_mensaje(self, remitente, mensaje, color):
        """Muestra un mensaje en el área de chat"""
        self.area_chat.config(state=tk.NORMAL)
        
        # Agregar remitente
        self.area_chat.insert(tk.END, f"{remitente}:\n", f"remitente_{color}")
        self.area_chat.tag_config(f"remitente_{color}", foreground=color, font=("Arial", 12, "bold"))
        
        # Agregar mensaje
        self.area_chat.insert(tk.END, f"{mensaje}\n\n")
        
        self.area_chat.config(state=tk.DISABLED)
        self.area_chat.see(tk.END)
    
    def enviar_mensaje(self):
        """Envía el mensaje del usuario"""
        mensaje = self.entrada_texto.get().strip()
        
        if not mensaje:
            return
        
        # Mostrar mensaje del usuario
        self.mostrar_mensaje("Tú", mensaje, "#2c3e50")
        self.entrada_texto.delete(0, tk.END)
        
        # Deshabilitar botones mientras procesa
        self.boton_enviar.config(state=tk.DISABLED)
        self.boton_mic.config(state=tk.DISABLED)
        self.entrada_texto.config(state=tk.DISABLED)
        
        # Mostrar indicador de "escribiendo..."
        self.area_chat.config(state=tk.NORMAL)
        self.area_chat.insert(tk.END, "Bagley está pensando...\n", "pensando")
        self.area_chat.tag_config("pensando", foreground="#95a5a6", font=("Arial", 10, "italic"))
        self.area_chat.config(state=tk.DISABLED)
        self.area_chat.see(tk.END)
        
        # Procesar en hilo separado
        threading.Thread(target=self.procesar_respuesta, args=(mensaje,), daemon=True).start()
    
    def procesar_respuesta(self, mensaje):
        """Procesa la respuesta de Bagley en segundo plano"""
        try:
            # Generar respuesta
            modelo = genai.GenerativeModel('models/gemini-2.0-flash')
            
            # Construir contexto con el prompt del modo actual
            contexto = self.prompts[self.modo_actual] + "\n\n"
            
            # Agregar historial reciente
            for msg in self.historial[-6:]:
                contexto += f"{msg['role']}: {msg['content']}\n"
            contexto += f"Usuario: {mensaje}\nBagley:"
            
            respuesta = modelo.generate_content(contexto)
            texto_respuesta = respuesta.text.strip()
            
            # Guardar en historial
            self.historial.append({"role": "Usuario", "content": mensaje})
            self.historial.append({"role": "Bagley", "content": texto_respuesta})
            
            # Actualizar UI en hilo principal
            self.ventana.after(0, self.mostrar_respuesta_bagley, texto_respuesta)
        
        except Exception as e:
            error_msg = f"Lo siento, tuve un problema: {str(e)}"
            self.ventana.after(0, self.mostrar_respuesta_bagley, error_msg)
    
    def mostrar_respuesta_bagley(self, respuesta):
        """Muestra la respuesta de Bagley"""
        # Eliminar "pensando..."
        self.area_chat.config(state=tk.NORMAL)
        content = self.area_chat.get("1.0", tk.END)
        if "Bagley está pensando..." in content:
            lines = content.split('\n')
            for i in range(len(lines)-1, -1, -1):
                if "Bagley está pensando..." in lines[i]:
                    del lines[i]
                    break
            self.area_chat.delete("1.0", tk.END)
            self.area_chat.insert("1.0", '\n'.join(lines))
        self.area_chat.config(state=tk.DISABLED)
        
        # Color según modo
        colores = {
            "psicologo": "#3498db",
            "deberes": "#e67e22",
            "programacion": "#9b59b6"
        }
        
        # Mostrar respuesta
        self.mostrar_mensaje("Bagley", respuesta, colores[self.modo_actual])
        
        # Hacer que Bagley hable la respuesta
        self.hablar(respuesta)
        
        # Habilitar botones
        self.boton_enviar.config(state=tk.NORMAL)
        self.boton_mic.config(state=tk.NORMAL)
        self.entrada_texto.config(state=tk.NORMAL)
        self.entrada_texto.focus()
    
    def ejecutar(self):
        """Inicia la aplicación"""
        self.ventana.mainloop()


# Iniciar la aplicación
if __name__ == "__main__":
    try:
        app = BagleyGUI()
        app.ejecutar()
    except Exception as e:
        print(f"Error al iniciar: {e}")
        print("\nAsegúrate de tener instaladas las librerías:")
        print("pip install pillow SpeechRecognition pyttsx3 pyaudio")    


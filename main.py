import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
import os
import threading

class ConversorVideoGIF:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Vídeo para GIF")
        self.root.geometry("500x300")
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Botão para selecionar arquivo
        ttk.Button(main_frame, text="Selecionar Vídeo", command=self.selecionar_video).grid(row=0, column=0, pady=10)
        
        # Label para mostrar o arquivo selecionado
        self.arquivo_label = ttk.Label(main_frame, text="Nenhum arquivo selecionado")
        self.arquivo_label.grid(row=1, column=0, pady=5)

        # Barra de progresso
        self.progresso = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progresso.grid(row=2, column=0, pady=10)

        # Botão de conversão
        self.btn_converter = ttk.Button(main_frame, text="Converter para GIF", command=self.converter_para_gif, state='disabled')
        self.btn_converter.grid(row=3, column=0, pady=10)

    def selecionar_video(self):
        # Filtros para tipos de arquivo de vídeo comuns
        filetypes = (
            ("Arquivos de vídeo", "*.mp4 *.avi *.mkv *.mov *.wmv"),
            ("Todos os arquivos", "*.*")
        )
        
        arquivo = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=filetypes
        )
        
        if arquivo:
            self.video_path = arquivo
            self.arquivo_label.config(text=os.path.basename(arquivo))
            self.btn_converter.config(state='normal')

    def atualizar_progresso(self, atual, total):
        progresso = (atual / total) * 100
        self.progresso['value'] = progresso
        self.root.update()

    def fazer_conversao(self, video, output_path):
        try:
            # Configurar o tamanho do vídeo
            width = min(480, video.w)  # Limita a largura máxima a 480px
            resized_video = video.resize(width=width)
            
            # Configurar a taxa de frames
            fps = min(15, video.fps)  # Limita o FPS a 15
            
            # Converter para GIF
            resized_video.write_gif(
                output_path,
                fps=fps,
                program='ffmpeg',
                opt='nq'
            )
            
            self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Conversão concluída com sucesso!"))
            self.root.after(0, lambda: self.btn_converter.config(state='normal'))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante a conversão: {str(e)}"))
            self.root.after(0, lambda: self.btn_converter.config(state='normal'))
        finally:
            try:
                video.close()
                resized_video.close()
            except:
                pass

    def converter_para_gif(self):
        try:
            # Carregar o vídeo
            video = VideoFileClip(self.video_path)
            
            # Verificar a duração
            if video.duration > 180:  # 3 minutos = 180 segundos
                messagebox.showerror("Erro", "O vídeo deve ter no máximo 3 minutos de duração!")
                video.close()
                return

            # Selecionar local para salvar o GIF
            output_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=[("GIF files", "*.gif")],
                title="Salvar GIF como"
            )

            if output_path:
                # Atualizar interface
                self.btn_converter.config(state='disabled')
                self.progresso['value'] = 0
                self.root.update()

                # Iniciar a conversão em uma thread separada
                thread = threading.Thread(
                    target=self.fazer_conversao,
                    args=(video, output_path)
                )
                thread.start()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao preparar a conversão: {str(e)}")
            self.btn_converter.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorVideoGIF(root)
    root.mainloop()
import { Attachment } from '../types';

/**
 * Servicio para manejar la carga y procesamiento de archivos
 * Gestiona diferentes tipos de archivos y su procesamiento
 */
class FileHandlerService {
  private readonly SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  private readonly SUPPORTED_DOCUMENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ];
  private readonly MAX_FILE_SIZE = parseInt(import.meta.env.VITE_MAX_FILE_SIZE);

  /**
   * Procesa un archivo y lo prepara para su uso
   */
  async processFile(file: File): Promise<Attachment> {
    try {
      // Validar archivo
      await this.validateFile(file);

      // Procesar según tipo
      if (this.SUPPORTED_IMAGE_TYPES.includes(file.type)) {
        return await this.processImage(file);
      } else if (this.SUPPORTED_DOCUMENT_TYPES.includes(file.type)) {
        return await this.processDocument(file);
      }

      throw new Error('Tipo de archivo no soportado');

    } catch (error) {
      console.error('Error al procesar archivo:', error);
      throw error;
    }
  }

  /**
   * Valida un archivo antes de procesarlo
   */
  private async validateFile(file: File): Promise<void> {
    // Validar tamaño
    if (file.size > this.MAX_FILE_SIZE) {
      throw new Error(`El archivo excede el tamaño máximo permitido (${this.MAX_FILE_SIZE / 1024 / 1024}MB)`);
    }

    // Validar tipo
    const isSupported = [
      ...this.SUPPORTED_IMAGE_TYPES,
      ...this.SUPPORTED_DOCUMENT_TYPES
    ].includes(file.type);

    if (!isSupported) {
      throw new Error('Tipo de archivo no soportado');
    }

    // Validar integridad
    const isValid = await this.validateFileIntegrity(file);
    if (!isValid) {
      throw new Error('El archivo está corrupto o no es válido');
    }
  }

  /**
   * Valida la integridad de un archivo
   */
  private async validateFileIntegrity(file: File): Promise<boolean> {
    try {
      // Verificar que el archivo se puede leer
      const buffer = await file.arrayBuffer();
      
      // Verificar firma de archivo según tipo
      if (this.SUPPORTED_IMAGE_TYPES.includes(file.type)) {
        return this.validateImageSignature(new Uint8Array(buffer));
      }

      if (file.type === 'application/pdf') {
        return this.validatePDFSignature(new Uint8Array(buffer));
      }

      // Para otros tipos, verificar que al menos tenga contenido
      return buffer.byteLength > 0;

    } catch (error) {
      console.error('Error al validar integridad:', error);
      return false;
    }
  }

  /**
   * Valida la firma de una imagen
   */
  private validateImageSignature(bytes: Uint8Array): boolean {
    // Firmas comunes de formatos de imagen
    const signatures = {
      jpeg: [0xFF, 0xD8, 0xFF],
      png: [0x89, 0x50, 0x4E, 0x47],
      gif: [0x47, 0x49, 0x46, 0x38]
    };

    // Verificar firmas conocidas
    return Object.values(signatures).some(signature =>
      signature.every((byte, i) => bytes[i] === byte)
    );
  }

  /**
   * Valida la firma de un PDF
   */
  private validatePDFSignature(bytes: Uint8Array): boolean {
    const pdfSignature = [0x25, 0x50, 0x44, 0x46]; // %PDF
    return pdfSignature.every((byte, i) => bytes[i] === byte);
  }

  /**
   * Procesa una imagen
   */
  private async processImage(file: File): Promise<Attachment> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          // Crear objeto URL para la imagen
          const url = URL.createObjectURL(file);

          // Crear miniatura
          const thumbnail = await this.createImageThumbnail(file);

          resolve({
            id: Date.now().toString(),
            type: 'image',
            url,
            thumbnailUrl: thumbnail,
            name: file.name,
            size: file.size,
            mimeType: file.type
          });
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Error al leer el archivo'));
      reader.readAsArrayBuffer(file);
    });
  }

  /**
   * Crea una miniatura de una imagen
   */
  private async createImageThumbnail(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            reject(new Error('No se pudo crear el contexto 2D'));
            return;
          }

          // Calcular dimensiones de la miniatura
          const MAX_SIZE = 200;
          let width = img.width;
          let height = img.height;
          
          if (width > height) {
            if (width > MAX_SIZE) {
              height *= MAX_SIZE / width;
              width = MAX_SIZE;
            }
          } else {
            if (height > MAX_SIZE) {
              width *= MAX_SIZE / height;
              height = MAX_SIZE;
            }
          }

          canvas.width = width;
          canvas.height = height;

          // Dibujar miniatura
          ctx.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL('image/jpeg', 0.7));
        };
        img.onerror = () => reject(new Error('Error al cargar la imagen'));
        img.src = e.target?.result as string;
      };
      reader.onerror = () => reject(new Error('Error al leer el archivo'));
      reader.readAsDataURL(file);
    });
  }

  /**
   * Procesa un documento
   */
  private async processDocument(file: File): Promise<Attachment> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const url = URL.createObjectURL(file);
        resolve({
          id: Date.now().toString(),
          type: 'document',
          url,
          name: file.name,
          size: file.size,
          mimeType: file.type
        });
      };
      reader.onerror = () => reject(new Error('Error al leer el documento'));
      reader.readAsArrayBuffer(file);
    });
  }

  /**
   * Libera recursos asociados a un archivo
   */
  releaseFile(url: string): void {
    URL.revokeObjectURL(url);
  }
}

// Exportar una instancia única del servicio
export const fileHandlerService = new FileHandlerService();

"""
Definerer grid-strukturer for numeriske beregninger.
"""

class Grid2D:
    """
    Definerer et 2D-grid for numeriske beregninger av en plate.
    
    Gridet deler platen inn i rektangulære kontrollvolumer.
    - Lengde (length) korresponderer med X-aksen.
    - Bredde (width) korresponderer med Y-aksen.
    """
    def __init__(self, width: float, length: float, 
                 width_segments: int, length_segments: int):
        """
        Initialiserer 2D-gridet.
        
        Args:
            width: Total bredde på gridet (Y-retning) [m].
            length: Total lengde på gridet (X-retning) [m].
            width_segments: Antall segmenter i bredderetningen.
            length_segments: Antall segmenter i lengderetningen.
        """
        self.width = width
        self.length = length
        self.width_segments = width_segments
        self.length_segments = length_segments
        
        if width_segments <= 0 or length_segments <= 0:
            raise ValueError("Antall segmenter må være positive heltall.")
            
        self.dy = width / width_segments
        self.dx = length / length_segments

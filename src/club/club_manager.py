from ..utils.writer import Writer

class ClubManager:
    def __init__(self):
        self.writer = Writer()
    
    def create_club_packet(self, club_name: str, description: str):
        """Yeni kulüp oluşturma paketi oluşturur"""
        w = Writer()
        
        # Kulüp adı ve açıklaması
        w.buffer += w.writeString(club_name)
        w.buffer += w.writeString(description)
        
        # Kulüp özellikleri
        w.buffer += w.writeVInt(1)  # Badge Identifier
        w.buffer += w.writeVInt(1)  # Badge ID
        w.buffer += w.writeVInt(2)  # Club type (Only creator can join)
        w.buffer += w.writeVInt(0)  # Trophy required (0 trophies needed)
        w.buffer += w.writeVInt(1)  # Family friendly
        
        return self._create_header(14301, w.buffer)
    
    def join_club_by_id_packet(self, club_high_id: int, club_low_id: int):
        """Kulübe ID ile katılma paketi oluşturur"""
        w = Writer()
        
        # Club ID'leri
        w.buffer += w.writeInt(club_high_id)
        w.buffer += w.writeInt(club_low_id)
        
        return self._create_header(14306, w.buffer)
    
    def join_club_by_tag_packet(self, club_tag: str):
        """Kulübe etiket ile katılma paketi oluşturur"""
        w = Writer()
        
        # # işaretini kaldır (eğer varsa)
        if club_tag.startswith('#'):
            club_tag = club_tag[1:]
        
        # Kulüp etiketi
        w.buffer += w.writeString(club_tag)
        
        return self._create_header(14303, w.buffer)
    
    def _create_header(self, message_id, data):
        """Paket başlığı oluşturur"""
        w = Writer()
        header = b''
        header += w.writeShort(message_id)
        header += len(data).to_bytes(3, 'big')
        header += w.writeShort(0)
        header += data
        return header 
from typing import Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Product:
    SerialNumber: str
    ModelSequence: List[int] = field(default_factory=list)
    TravelerID: Optional[str] = None
    CreationDate: Optional[datetime] = None

    CurrentStationID: Optional[int] = None
    StationSeqPos: Optional[int] = None
    BeginDateTime: Optional[datetime] = None
    EndDateTime: Optional[datetime] = None

    CurrentQueue_ArrivalTime: Optional[datetime] = None
    
    def get_remaining_operations(self) -> int:
        if self.StationSeqPos is None or not self.ModelSequence:
            return 0
        return len(self.ModelSequence) - self.StationSeqPos

    # For computing pressure in priority score
    def get_next_stations(self, num_ahead:int=2) -> List[int]:
        if self.StationSeqPos is None or not self.ModelSequence:
            return []
        NextStations = []
        # Get the next (num_ahead) stations in the sequence until end of model sequence
        for i in range(self.StationSeqPos + 1, min(self.StationSeqPos + 1 + num_ahead, len(self.ModelSequence))):
            NextStations.append(self.ModelSequence[i])
        return NextStations

@dataclass
class Worker:
    EmployeeID: str
    FirstName: str
    LastName: str

    AssignedStation: Optional[int] = None
    IsAvailable: bool = True
    CompetentStations: Set[int] = field(default_factory=set)
    
    @property
    def full_name(self) -> str:
        return f"{self.FirstName} {self.LastName}"

@dataclass
class Workstation:
    StationID: int
    StationName: str
    MaxQueueSize: int
    
    CurrentProduct: Optional[Product] = None
    CurrentWorker: Optional[Worker]=None
    Queue: deque[Product] = field(default_factory=deque)
    IsIdle: bool = True
    
    @property
    def get_queue_length(self) -> int:
        return len(self.Queue)
    
    @property
    def is_queue_full(self) -> bool:
        return self.get_queue_length >= self.MaxQueueSize

    def add_to_queue(self, product: Product) -> bool:
        if self.get_queue_length < self.MaxQueueSize:
            product.CurrentQueue_ArrivalTime = datetime.now()
            self.Queue.append(product)
            return True
        return False

    def remove_from_queue(self, product: Product) -> bool:
        try:
            self.Queue.remove(product)
            return True
        except ValueError:
            return False

    # Look at the product at the front of the queue without removing it
    def front_lookup(self) -> Optional[Product]:
        return self.Queue[0] if self.Queue else None

    def clear_current_assignment(self) -> None:
        self.CurrentProduct = None
        self.CurrentWorker = None
        self.IsIdle = True
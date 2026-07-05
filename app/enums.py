import enum


class NotificationType(str, enum.Enum):
    NEW_BID = "new_bid"
    BID_ACCEPTED = "bid_accepted"
    PROJECT_COMPLETED = "project_completed"
    RATING_RECEIVED = "rating_received"


class UserType(str, enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"
    FREELANCER = "freelancer"
    USER = "user"


class ProjectStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class BidStatus(str, enum.Enum):
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    PENDING = 'pending'

from .user import LoggedUserView, UpdateUserView, ChangePasswordView  # noqa: F401
from .canteen import (  # noqa: F401
    PublishedCanteensView,
    PublishedCanteenSingleView,
    UserCanteensView,
    RetrieveUpdateUserCanteenView,
    AddManagerView,
    RemoveManagerView,
    PublishCanteenView,
    UnpublishCanteenView,
    SendCanteenNotFoundEmail,
    UserCanteenPreviews,
    CanteenStatisticsView,
    CanteenLocationsView,
)
from .diagnostic import (  # noqa: F401
    DiagnosticCreateView,
    DiagnosticUpdateView,
    ImportDiagnosticsView,
    EmailDiagnosticImportFileView,
)
from .sector import SectorListView  # noqa: F401
from .blog import BlogPostsView, BlogPostView  # noqa: F401
from .subscription import SubscribeBetaTester, SubscribeNewsletter  # noqa: F401
from .teledeclaration import (  # noqa: F401
    TeledeclarationCreateView,
    TeledeclarationCancelView,
    TeledeclarationPdfView,
)
from .inquiry import InquiryView  # noqa: F401
from .purchase import (  # noqa: F401
    PurchaseListCreateView,
    PurchaseRetrieveUpdateDestroyView,
    CanteenPurchasesSummaryView,
    PurchaseListExportView,
    PurchaseOptionsView,
)
from .reservationexpe import ReservationExpeView  # noqa: F401
from .message import MessageCreateView  # noqa: F401

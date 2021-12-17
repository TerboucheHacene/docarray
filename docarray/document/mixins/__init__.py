from .attribute import GetAttributesMixin
from .audio import AudioDataMixin
from .buffer import BufferDataMixin
from .content import ContentPropertyMixin
from .convert import ConvertMixin
from .dump import DumpFileMixin
from .image import ImageDataMixin
from .mesh import MeshDataMixin
from .plot import PlotMixin
from .property import PropertyMixin
from .protobuf import ProtobufMixin
from .sugar import SingletonSugarMixin
from .text import TextDataMixin
from .video import VideoDataMixin


class AllMixins(
    ProtobufMixin,
    PropertyMixin,
    ContentPropertyMixin,
    ConvertMixin,
    AudioDataMixin,
    ImageDataMixin,
    TextDataMixin,
    MeshDataMixin,
    VideoDataMixin,
    BufferDataMixin,
    PlotMixin,
    DumpFileMixin,
    SingletonSugarMixin,
    GetAttributesMixin,
):
    """All plugins that can be used in :class:`Document`. """

    ...
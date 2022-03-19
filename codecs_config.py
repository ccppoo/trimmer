from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import subprocess
from typing import List, Dict, TypeVar, Callable, Union

__all__ = [
    "Codec",
    "Codecs",
    "CodecType",
    "current_pc_codec"
]

__CodecName = TypeVar("__CodecName", str, bytes)

class CodecType(Enum):
    Video = 0
    Audio = 1
    Subtitle = 2

@dataclass
class Codec:
    # FIXME : make this class immutable in future
    name : str
    decoding : bool
    encoding : bool
    type : CodecType
    Intra_frame_only : bool
    lossy_compression : bool
    lossless_compression : bool 

    def __init__(self, name: str, supports : str) -> None:
        '''
        D..... = Decoding supported
        .E.... = Encoding supported
        ..V... = Video codec
        ..A... = Audio codec
        ..S... = Subtitle codec
        ...I.. = Intra frame-only codec
        ....L. = Lossy compression
        .....S = Lossless compression
        '''
        self.name = name
        self.__set_values(supports.strip())

    def __set_values(self, supports : str) -> None:
        d, e, type_, i, l, s = supports
        isTrue = lambda x : x != '.'
        shortType = {"V" : CodecType.Video, "A" : CodecType.Audio, "S" : CodecType.Subtitle}
        self.decoding = isTrue(d)
        self.encoding = isTrue(e)
        self.type = shortType.get(type_)
        self.Intra_frame_only = isTrue(i)
        self.lossy_compression = isTrue(l)
        self.lossless_compression = isTrue(s)

class Codecs:
    __Codecs : Dict[__CodecName, Codec]

    def __init__(self, codecs : Union[Codec, List[Codec]] = None) -> None:
        if codecs is None:
            self.__Codecs = None
        
        if type(codecs) == Codec:
            self.__Codecs = {codecs.name : codecs}
        
        if type(codecs) == list:
            self.__Codecs = {codec.name : codec for codec in codecs}

    def __codec_filter(self, key : Callable) -> List[Codec]:
        return [codec_ for codec_ in filter(key, list(self.__Codecs.values()))]

    def __codec_type_filter(self, codecType : CodecType) -> List[Codec]:
        condition = lambda x : getattr(x, "type").value == codecType.value
        return [cdc for cdc in self.__codec_filter(key = condition)]

    def addCodec(self, codec : Codec) -> Codecs:
        assert type(codec) == Codec

        if self.__Codecs is None:
            self.__Codecs = {codec.name : codec}
            return self

        assert codec.name not in (self.__Codecs.keys() if self.__Codecs is not None else [])
        self.__Codecs.update({codec.name : codec})

        return self

    @property
    def decodable(self,) -> Codecs:
        condition = lambda x : getattr(x, "decoding")
        return Codecs(codecs = self.__codec_filter(key = condition))

    @property
    def encodable(self,) -> Codecs:
        condition = lambda x : getattr(x, "encoding")
        return Codecs(codecs = self.__codec_filter(key = condition))
    
    @property
    def audio_codecs(self, ) -> Codecs:
        return Codecs(self.__codec_type_filter(CodecType.Audio))
    
    @property
    def video_codecs(self, ) -> Codecs:
        return Codecs(self.__codec_type_filter(CodecType.Video))

    @property
    def subtitle_codecs(self, ) -> Codecs:
        return Codecs(self.__codec_type_filter(CodecType.Subtitle))

    @property
    def names(self, ) -> List[__CodecName]:
        return [cdc.name for cdc in self.__Codecs.values()]

    def __len__(self, ) -> int:
        return len(self.__Codecs.values())

    def __repr__(self, ) -> str:
        preview = ""
        if len(self.__Codecs) < 10:
            preview = ", ".join(self.names)
        else:
            preview = ", ".join(self.names[:5])
            preview += ", ... ,"
            preview += ", ".join(self.names[-5:])
            preview += f", and {len(self.__Codecs)-10} more codecs"

        return f"Numbers of Codec avaliable : {len(self.__Codecs.values())} Codecs : {preview}"

def current_pc_codec() -> Codecs:
    codecs = Codecs()

    # FIXME : hide ffmpeg message in console ("... Copyright (c) 2000-2022 the FFmpeg developers ... ")
    out = subprocess.check_output(["ffmpeg", "-codecs"], encoding='utf-8')

    CODEC_INFO = [line for line in out.split("\n")]
    CODEC_START = CODEC_INFO.index(" -------") + 1

    for line in CODEC_INFO[CODEC_START:]:
        if not len(line.strip()):
            continue
        supports, name = line.split()[:2]
        codecs.addCodec(Codec(name = name, supports=supports))
    
    return codecs
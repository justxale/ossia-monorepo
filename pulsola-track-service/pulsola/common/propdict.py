import typing


class PropDict:
    def __setitem__(self, key: str, value: typing.Any) -> None:
        self.__dict__[key] = value

    def __getitem__(self, item: str) -> typing.Any:
        return self.__dict__[item]

    def __setattr__(self, key: str, value: typing.Any) -> None:
        self.__dict__[key] = value

    def __getattr__(self, item: str) -> typing.Any:
        try:
            return self.__dict__[item]
        except KeyError:
            raise AttributeError()

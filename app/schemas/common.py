from typing import Annotated, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

class Schema(BaseModel):

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        #serialize_by_alias=True,
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

class UpdateSchema(Schema):
    nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def forbid_null(self) -> Self:
        for name in self.model_fields_set:
            if getattr(self, name) is None and name not in self.nullable_fields:
                alias = type(self).model_fields[name].alias or name
                raise ValueError(f"Поле {alias} не может быть null")
        return self

Id = Annotated[int, Field(gt=0)]
Rating = Annotated[int, Field(ge=1, le=5)]
Title = Annotated[str, Field(min_length=1, max_length=255)]
Content = Annotated[str, Field(min_length=1, max_length=10_000)]
OptionalContent = Annotated[str, Field(max_length=10_000)]
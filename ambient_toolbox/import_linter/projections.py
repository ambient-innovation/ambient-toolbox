import dataclasses


@dataclasses.dataclass(kw_only=True)
class ImportLinterContract:
    name: str
    type: str
    source_modules: str
    forbidden_modules: list[str]

    @classmethod
    def generate_contract(cls, app: str, forbidden_modules: list[str]):
        return cls(
            name=f"[GENERATED] Independent app {app!r} not allowed",
            type="forbidden",
            source_modules=app,
            forbidden_modules=forbidden_modules,
        )

    def to_dict(self):
        return {
            "name": f"[GENERATED] Independent app {self.source_modules!r} not allowed to know about other apps",
            "type": "forbidden",
            "source_modules": self.source_modules,
            "forbidden_modules": self.forbidden_modules,
        }

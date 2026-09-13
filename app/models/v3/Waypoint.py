from pydantic import BaseModel


class Waypoint(BaseModel):
    name: str
    initials: str
    x: int
    y: int
    z: int
    color: int
    disabled: bool = False
    type: int = 0
    set: str = "gui.xaero_default"
    rotate_on_tp: bool = False
    tp_yaw: int = 0
    visibility_type: int = 0
    destination: bool = False

    def to_line(self) -> str:
        return ":".join(
            [
                "waypoint",
                self.name,
                self.initials,
                str(self.x),
                str(self.y),
                str(self.z),
                str(self.color),
                str(self.disabled).lower(),
                str(self.type),
                self.set,
                str(self.rotate_on_tp).lower(),
                str(self.tp_yaw),
                str(self.visibility_type),
                str(self.destination).lower(),
            ]
        )

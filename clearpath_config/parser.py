from clearpath_config.common import (
    Platform,
    Accessory
)
from clearpath_config.clearpath_config import ClearpathConfig
from clearpath_config.mounts.mounts import (
    MountsConfig,
    Mount,
    BaseMount,
    FlirPTU,
    FathPivot
)
from clearpath_config.platform.base import BaseDecorationsConfig
from clearpath_config.platform.decorations import (
    Bumper,
    TopPlate
)
from clearpath_config.mounts.pacs import PACS
from clearpath_config.platform.platform import PlatformConfig
from clearpath_config.platform.a200 import A200DecorationsConfig
from clearpath_config.platform.j100 import J100DecorationsConfig
from clearpath_config.sensors.sensors import (
    Sensor,
    BaseSensor,
    Camera,
    BaseCamera,
    BlackflyCamera,
    RealsenseCamera,
    Lidar2D,
    BaseLidar2D,
    SensorConfig
)
from clearpath_config.system.system import SystemConfig, HostsConfig, Host
from typing import List
import os
import yaml


class BaseConfigParser:
    @staticmethod
    def check_key_exists(key: str, config: dict) -> bool:
        return key in config

    @staticmethod
    def assert_key_exists(key: str, config: dict) -> None:
        assert BaseConfigParser.check_key_exists(
            key, config
        ), "Key '%s' must be in YAML" % key

    @staticmethod
    def get_required_val(key: str, config: dict):
        BaseConfigParser.assert_key_exists(key, config)
        return config[key]

    @staticmethod
    def get_optional_val(key: str, config: dict, default=None):
        if BaseConfigParser.check_key_exists(key, config):
            return config[key]
        else:
            return default


class HostsConfigParser(BaseConfigParser):
    # Key
    HOSTS = "hosts"
    # Host Keys
    PLATFORM = "platform"
    ONBOARD = "onboard"
    REMOTE = "remote"

    def __new__(cls, config: dict) -> HostsConfig:
        htsconfig = HostsConfig()
        # Hosts
        hosts = cls.get_required_val(cls.HOSTS, config)
        # Hosts.Platform
        platform = cls.get_platform_host(config=hosts)
        htsconfig.set_platform(platform)
        # Hosts.Onboard
        htsconfig.set_onboard(cls.get_hostlists(cls.ONBOARD, hosts))
        # Hosts.Remote
        htsconfig.set_remote(cls.get_hostlists(cls.REMOTE, hosts))
        return htsconfig

    @classmethod
    def get_platform_host(cls, config) -> Host:
        platform = cls.get_required_val(cls.PLATFORM, config)
        assert isinstance(platform, dict), "Platform host must be a dictionary"
        entries = list(platform.items())
        assert (
            len(entries) == 1
        ), "Platform must have exactly one ('hostname': 'ip') entry"
        hostname, ip = entries[0]
        return Host(hostname, ip)

    @classmethod
    def get_hostlists(cls, key, config) -> List[Host]:
        hostlist = cls.get_optional_val(key, config)
        if not hostlist:
            return []
        assert isinstance(hostlist, dict), (
            "%s host list must be a dictionary" % key.title()
        )
        hosts = []
        for hostname, value in hostlist.items():
            hosts.append(Host(hostname, value))
        return hosts


class SystemConfigParser(BaseConfigParser):
    # Key
    SYSTEM = "system"
    # System Keys
    SELF = "self"
    HOSTS = "hosts"

    def __new__(cls, config: dict) -> SystemConfig:
        sysconfig = SystemConfig()
        # System
        system = cls.get_required_val(cls.SYSTEM, config)
        # System.Self
        sysconfig.set_self(cls.get_required_val(cls.SELF, system))
        # System.Hosts
        sysconfig.set_hosts(HostsConfigParser(system))
        return sysconfig


class BumperConfigParser(BaseConfigParser):
    # Bumper Keys
    ENABLED = "enabled"
    EXTENSION = "extension"
    MODEL = "model"

    def __new__(cls, key: str, config: dict) -> Bumper:
        bmpconfig = Bumper(key)
        # Bumper
        bumper = cls.get_optional_val(key, config)
        if not bumper:
            return bmpconfig
        # Bumper.Enable
        if cls.get_optional_val(cls.ENABLED, bumper, True):
            bmpconfig.enable()
        else:
            bmpconfig.disable()
        # Bumper.Extension
        bmpconfig.set_extension(cls.get_required_val(cls.EXTENSION, bumper))
        # Bumper.Model
        bmpconfig.set_model(cls.get_required_val(cls.MODEL, bumper))
        return bmpconfig


class TopPlateConfigParser(BaseConfigParser):
    # Top Plate Keys
    ENABLED = "enabled"
    MODEL = "model"

    def __new__(cls, key: str, config: dict) -> TopPlate:
        topconfig = TopPlate(key)
        # Top_Plate
        top_plate = cls.get_optional_val(key, config)
        if not top_plate:
            return topconfig
        # Top_Plate.Enable
        if cls.get_optional_val(cls.ENABLED, top_plate, True):
            topconfig.enable()
        else:
            topconfig.disable()
        # Top_Plate.Model
        topconfig.set_model(cls.get_required_val(cls.MODEL, top_plate))
        return topconfig


class DecorationsConfigParser(BaseConfigParser):
    # Key
    DECORATIONS = "decorations"

    class A200:
        # A200 Husky Decoration Keys
        FRONT_BUMPER = "front_bumper"
        REAR_BUMPER = "rear_bumper"
        TOP_PLATE = "top_plate"
        PACS = "pacs"

        def __new__(cls, config: dict) -> A200DecorationsConfig:
            dcnconfig = A200DecorationsConfig()
            dcnparser = DecorationsConfigParser
            # Decorations
            decorations = (
                dcnparser.get_required_val(dcnparser.DECORATIONS, config))
            # Decorations.Front_Bumper
            dcnconfig.set_bumper(
                BumperConfigParser(cls.FRONT_BUMPER, decorations))
            # Decorations.Rear_Bumper
            dcnconfig.set_bumper(
                BumperConfigParser(cls.REAR_BUMPER, decorations))
            # Decorations.Top_Plate
            dcnconfig.set_top_plate(
                TopPlateConfigParser(cls.TOP_PLATE, decorations))
            return dcnconfig

    class J100:
        # J100 Jackal Decoration Keys
        FRONT_BUMPER = "front_bumper"
        REAR_BUMPER = "rear_bumper"

        def __new__(cls, config: dict) -> J100DecorationsConfig:
            dcnconfig = J100DecorationsConfig()
            dcnparser = DecorationsConfigParser
            # Decorations
            decorations = (
                dcnparser.get_required_val(dcnparser.DECORATIONS, config))
            # Decorations.Front_Bumper
            dcnconfig.set_bumper(
                BumperConfigParser(cls.FRONT_BUMPER, decorations))
            # Decorations.Rear_Bumper
            dcnconfig.set_bumper(
                BumperConfigParser(cls.REAR_BUMPER, decorations))
            return dcnconfig

    MODEL_CONFIGS = {Platform.A200: A200, Platform.J100: J100}

    def __new__(cls, model: str, config: dict) -> BaseDecorationsConfig:
        assert model in Platform.ALL, "Model '%s' must be one of %s" % (
            model,
            Platform.ALL,
        )
        return DecorationsConfigParser.MODEL_CONFIGS[model](config)


class PlatformConfigParser(BaseConfigParser):
    # Key
    PLATFORM = "platform"
    # Platform Keys
    SERIAL_NUMBER = "serial_number"
    DECORATIONS = "decorations"
    EXTRAS = "extras"
    # Platform Extras KEys
    URDF = "urdf"
    CONTROL = "control"

    def __new__(cls, config: dict) -> PlatformConfig:
        pfmconfig = PlatformConfig()
        # Platform
        platform = cls.get_required_val(cls.PLATFORM, config)
        # Platform.SerialNumber
        pfmconfig.set_serial_number(
            cls.get_required_val(cls.SERIAL_NUMBER, platform))
        # Platform.Decorations
        pfmconfig.decorations = (
            DecorationsConfigParser(pfmconfig.get_model(), platform))
        # Platform.Extras
        extras = cls.get_optional_val(cls.EXTRAS, platform)
        if extras:
            pfmconfig.extras.set_urdf_extras(
                cls.get_optional_val(cls.URDF, extras, ""))
            pfmconfig.extras.set_control_extras(
                cls.get_optional_val(cls.CONTROL, extras, ""))
        return pfmconfig


class AccessoryParser(BaseConfigParser):
    # Keys
    NAME = "name"
    PARENT = "parent"
    XYZ = "xyz"
    RPY = "rpy"

    def __new__(cls, config: dict) -> Accessory:
        name = cls.get_required_val(
            AccessoryParser.NAME, config)
        parent = cls.get_optional_val(
            AccessoryParser.PARENT, config, Accessory.PARENT)
        xyz = cls.get_optional_val(
            AccessoryParser.XYZ, config, Accessory.XYZ)
        rpy = cls.get_optional_val(
            AccessoryParser.RPY, config, Accessory.RPY)
        return Accessory(name, parent, xyz, rpy)


class MountParser(BaseConfigParser):

    class Base(BaseConfigParser):
        # Keys
        MODEL = "model"

        def __new__(cls, config: dict) -> BaseMount:
            parent = cls.get_optional_val(
                AccessoryParser.PARENT, config, Accessory.PARENT)
            xyz = cls.get_optional_val(
                AccessoryParser.XYZ, config, Accessory.XYZ)
            rpy = cls.get_optional_val(
                AccessoryParser.RPY, config, Accessory.RPY)
            return BaseMount(
                parent=parent,
                xyz=xyz,
                rpy=rpy,
                )

    class FathPivot(BaseConfigParser):
        # Keys
        ANGLE = "angle"

        def __new__(cls, config: dict) -> FathPivot:
            b = MountParser.Base(config)
            # Pivot Angle
            angle = cls.get_optional_val(
                MountParser.FathPivot.ANGLE,
                config,
                FathPivot.ANGLE,
            )
            return FathPivot(
                parent=b.get_parent(),
                xyz=b.get_xyz(),
                rpy=b.get_rpy(),
                angle=angle,
            )

    class FlirPTU(BaseConfigParser):
        # Keys
        TTY_PORT = "tty_port"
        TCP_PORT = "tcp_port"
        IP_ADDRESS = "ip"
        CONNECTION_TYPE = "connection_type"
        LIMITS_ENABLED = "limits_enabled"

        def __new__(cls, config: dict) -> FlirPTU:
            b = MountParser.Base(config)
            # TTY Port
            tty_port = cls.get_optional_val(
                MountParser.FlirPTU.TTY_PORT,
                config,
                FlirPTU.TTY_PORT,
            )
            # TCP Port
            tcp_port = cls.get_optional_val(
                MountParser.FlirPTU.TCP_PORT,
                config,
                FlirPTU.TCP_PORT,
            )
            # IP Address
            ip = cls.get_optional_val(
                MountParser.FlirPTU.IP_ADDRESS,
                config,
                FlirPTU.IP_ADDRESS,
            )
            # Connection Type
            connection_type = cls.get_optional_val(
                MountParser.FlirPTU.CONNECTION_TYPE,
                config,
                FlirPTU.CONNECTION_TYPE
            )
            # Limits Enabled
            limits_enabled = cls.get_optional_val(
                MountParser.FlirPTU.LIMITS_ENABLED,
                config,
                FlirPTU.LIMITS_ENABLED,
            )
            return FlirPTU(
                parent=b.get_parent(),
                xyz=b.get_xyz(),
                rpy=b.get_rpy(),
                tty_port=tty_port,
                tcp_port=tcp_port,
                ip=ip,
                connection_type=connection_type,
                limits_enabled=limits_enabled,
            )

    class PACSRiser(BaseConfigParser):
        # Keys
        ROWS = "rows"
        COLUMNS = "columns"
        THICKNESS = "thickness"

        def __new__(cls, config: dict) -> PACS.Riser:
            b = MountParser.Base(config)
            # Rows
            rows = cls.get_required_val(
                MountParser.PACSRiser.ROWS,
                config
            )
            # Columns
            columns = cls.get_required_val(
                MountParser.PACSRiser.COLUMNS,
                config
            )
            # Thickness
            thickness = cls.get_optional_val(
                MountParser.PACSRiser.THICKNESS,
                config,
                PACS.Riser.THICKNESS
            )
            return PACS.Riser(
                rows=rows,
                columns=columns,
                thickness=thickness,
                parent=b.get_parent(),
                xyz=b.get_xyz(),
                rpy=b.get_rpy(),
            )

    class PACSBracket(BaseConfigParser):
        # Keys
        MODEL = "model"

        def __new__(cls, config: dict) -> PACS.Riser:
            b = MountParser.Base(config)
            # Model
            model = cls.get_optional_val(
                MountParser.PACSBracket.MODEL,
                config,
                PACS.Bracket.DEFAULT
            )
            return PACS.Bracket(
                model=model,
                parent=b.get_parent(),
                xyz=b.get_xyz(),
                rpy=b.get_rpy(),
            )

    MODELS = {
        Mount.FATH_PIVOT: FathPivot,
        Mount.FLIR_PTU: FlirPTU,
        Mount.PACS_RISER: PACSRiser,
        Mount.PACS_BRACKET: PACSBracket
    }

    def __new__(cls, model, config: dict) -> BaseMount:
        assert model in MountParser.MODELS, (
            "Model '%s' must be one of '%s'" % (
                model,
                MountParser.MODELS
            )
        )
        return cls.MODELS[model](config)


class MountsConfigParser(BaseConfigParser):
    # Key
    MOUNTS = "mounts"
    MOUNT_CONFIG = {}

    def __new__(cls, config: dict) -> MountsConfig:
        mntconfig = MountsConfig()
        # Mounts
        mounts = cls.get_optional_val(cls.MOUNTS, config)
        mntconfig.set_fath_pivots(cls.get_mounts(mounts, Mount.FATH_PIVOT))
        mntconfig.set_flir_ptus(cls.get_mounts(mounts, Mount.FLIR_PTU))
        mntconfig.set_risers(cls.get_mounts(mounts, Mount.PACS_RISER))
        mntconfig.set_brackets(cls.get_mounts(mounts, Mount.PACS_BRACKET))
        return mntconfig

    @classmethod
    def get_mounts(cls, config: dict, model: str) -> List[Mount]:
        # Assert Dictionary
        assert isinstance(config, dict), (
            "Mounts must be a dictionary of lists"
        )
        entries = cls.get_optional_val(model, config, [])
        # Assert List
        assert isinstance(entries, list), (
            "Model entries must be in a list"
        )
        models = []
        for entry in entries:
            models.append(MountParser(model, entry))
        return models


class BaseSensorParser(BaseConfigParser):
    # Keys
    URDF_ENABLED = "urdf_enabled"
    LAUNCH_ENABLED = "launch_enabled"

    def __new__(cls, config: dict) -> BaseSensor:
        parent = cls.get_optional_val(
            AccessoryParser.PARENT, config, AccessoryParser.PARENT)
        xyz = cls.get_optional_val(
            AccessoryParser.XYZ, config, Accessory.XYZ)
        rpy = cls.get_optional_val(
            AccessoryParser.RPY, config, Accessory.RPY)
        urdf_enabled = cls.get_optional_val(
            BaseSensorParser.URDF_ENABLED, config, BaseSensor.URDF_ENABLED)
        launch_enabled = cls.get_optional_val(
            BaseSensorParser.LAUNCH_ENABLED, config, BaseSensor.LAUNCH_ENABLED)
        return BaseSensor(
            parent=parent,
            xyz=xyz, rpy=rpy,
            urdf_enabled=urdf_enabled,
            launch_enabled=launch_enabled
        )


class BaseLidar2DParser(BaseConfigParser):
    # Keys
    IP = "ip"
    PORT = "port"
    MIN_ANGLE = "min_angle"
    MAX_ANGLE = "max_angle"

    def __new__(cls, config: dict) -> BaseLidar2D:
        sensor = BaseSensorParser(config)
        ip = cls.get_optional_val(
            BaseLidar2DParser.IP, config, BaseLidar2D.IP_ADDRESS)
        port = cls.get_optional_val(
            BaseLidar2DParser.PORT, config, BaseLidar2D.IP_PORT)
        min_angle = cls.get_optional_val(
            BaseLidar2DParser.MIN_ANGLE, config, BaseLidar2D.MIN_ANGLE)
        max_angle = cls.get_optional_val(
            BaseLidar2DParser.MAX_ANGLE, config, BaseLidar2D.MAX_ANGLE)
        return BaseLidar2D(
            parent=sensor.get_parent(),
            xyz=sensor.get_xyz(),
            rpy=sensor.get_rpy(),
            urdf_enabled=sensor.get_urdf_enabled(),
            launch_enabled=sensor.get_launch_enabled(),
            ip=ip,
            port=port,
            min_angle=min_angle,
            max_angle=max_angle
        )


class Lidar2DParser(BaseConfigParser):
    MODEL = "model"

    def __new__(cls, config: dict) -> BaseLidar2D:
        base = BaseLidar2DParser(config)
        model = cls.get_required_val(Lidar2DParser.MODEL, config)
        lidar2d = Lidar2D(model)
        # Set Base Parameters
        lidar2d.set_parent(base.get_parent())
        lidar2d.set_xyz(base.get_xyz())
        lidar2d.set_rpy(base.get_rpy())
        lidar2d.set_urdf_enabled(base.get_urdf_enabled())
        lidar2d.set_launch_enabled(base.get_launch_enabled())
        lidar2d.set_ip(base.get_ip())
        lidar2d.set_port(base.get_port())
        lidar2d.set_min_angle(base.get_min_angle())
        lidar2d.set_max_angle(base.get_max_angle())
        return lidar2d


class BaseCameraParser(BaseConfigParser):
    FPS = "fps"
    SERIAL = "serial"

    def __new__(cls, config: dict) -> BaseCamera:
        sensor = BaseSensorParser(config)
        fps = cls.get_optional_val(
            BaseCameraParser.FPS, config, BaseCamera.FPS)
        serial = cls.get_optional_val(
            BaseCameraParser.SERIAL, config, BaseCamera.SERIAL)
        return BaseCamera(
            parent=sensor.get_parent(),
            xyz=sensor.get_xyz(),
            rpy=sensor.get_rpy(),
            urdf_enabled=sensor.get_urdf_enabled(),
            launch_enabled=sensor.get_launch_enabled(),
            fps=fps,
            serial=serial
        )


class CameraParser(BaseConfigParser):
    MODEL = "model"

    # Blackfly Parameters
    CONNECTION_TYPE = "connection_type"
    ENCODING = "encoding"

    # Realsense Parameters
    WIDTH = "width"
    HEIGHT = "height"
    DEPTH_ENABLED = "depth_enabled"
    DEPTH_FPS = "depth_fps"
    DEPTH_WIDTH = "depth_width"
    DEPTH_HEIGHT = "depth_height"

    def __new__(cls, config: dict) -> BaseLidar2D:
        base = BaseCameraParser(config)
        model = cls.get_required_val(CameraParser.MODEL, config)
        camera = Camera(model)
        # Set Base Parameters
        camera.set_parent(base.get_parent())
        camera.set_xyz(base.get_xyz())
        camera.set_rpy(base.get_rpy())
        camera.set_urdf_enabled(base.get_urdf_enabled())
        camera.set_launch_enabled(base.get_launch_enabled())
        camera.set_fps(base.get_fps())
        camera.set_serial(base.get_serial())
        # Set Specific Parameters
        if model == Camera.BLACKFLY:
            camera.set_connection_type(
                cls.get_optional_val(
                    CameraParser.CONNECTION_TYPE,
                    config,
                    BlackflyCamera.CONNECTION_TYPE
                )
            )
            camera.set_encoding(
                cls.get_optional_val(
                    CameraParser.ENCODING,
                    config,
                    BlackflyCamera.BAYER_RG8
                )
            )
        elif model == Camera.REALSENSE:
            camera.set_width(
                cls.get_optional_val(
                    CameraParser.WIDTH,
                    config,
                    RealsenseCamera.WIDTH
                )
            )
            camera.set_height(
                cls.get_optional_val(
                    CameraParser.HEIGHT,
                    config,
                    RealsenseCamera.HEIGHT
                )
            )
            camera.set_depth_enabled(
                cls.get_optional_val(
                    CameraParser.DEPTH_ENABLED,
                    config,
                    RealsenseCamera.DEPTH_ENABLED
                )
            )
            camera.set_depth_fps(
                cls.get_optional_val(
                    CameraParser.DEPTH_FPS,
                    config,
                    RealsenseCamera.DEPTH_FPS
                )
            )
            camera.set_depth_width(
                cls.get_optional_val(
                    CameraParser.DEPTH_WIDTH,
                    config,
                    RealsenseCamera.DEPTH_WIDTH
                )
            )
            camera.set_depth_height(
                cls.get_optional_val(
                    CameraParser.DEPTH_HEIGHT,
                    config,
                    RealsenseCamera.DEPTH_HEIGHT
                )
            )
        return camera


class SensorParser(BaseConfigParser):

    def __new__(cls, model: str, config: dict) -> BaseSensor:
        Sensor.assert_type(model)
        if model == Sensor.LIDAR2D:
            return Lidar2DParser(config)
        elif model == Sensor.CAMERA:
            return CameraParser(config)


class SensorConfigParser(BaseConfigParser):
    # Key
    SENSORS = "sensors"

    def __new__(cls, config: dict) -> SensorConfig:
        snrconfig = SensorConfig()
        # Sensors
        sensors = cls.get_optional_val(cls.SENSORS, config)
        if not sensors:
            return snrconfig
        # Lidar2D
        snrconfig.set_all_lidar_2d(cls.get_sensors(sensors, Sensor.LIDAR2D))
        # Camera
        snrconfig.set_all_camera(cls.get_sensors(sensors, Sensor.CAMERA))
        return snrconfig

    @classmethod
    def get_sensors(cls, config: dict, model: str) -> List[BaseSensor]:
        entries = cls.get_optional_val(model, config, [])
        models = []
        for entry in entries:
            models.append(SensorParser(model, entry))
        return models


# Clearpath Configuration Parser
class ClearpathConfigParser(BaseConfigParser):
    @staticmethod
    # Get Valid Path
    def find_valid_path(path, cwd=None):
        abspath = path
        if cwd:
            relpath = os.path.join(cwd, path)
        else:
            relpath = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), path)
        if not os.path.isfile(abspath) and not os.path.isfile(relpath):
            return None
        if os.path.isfile(abspath):
            path = abspath
        elif os.path.isfile(relpath):
            path = relpath
        return path

    @staticmethod
    def read_yaml(path: str) -> dict:
        # Check YAML Path
        path = ClearpathConfigParser.find_valid_path(path, os.getcwd())
        assert path, "YAML file '%s' could not be found" % path
        # Check YAML can be Opened
        try:
            config = yaml.load(open(path), Loader=yaml.SafeLoader)
        except yaml.scanner.ScannerError:
            raise AssertionError(
                "YAML file '%s' is not well formed" % path)
        except yaml.constructor.ConstructorError:
            raise AssertionError(
                "YAML file '%s' is attempting to create unsafe objects" % (
                    path))
        # Check contents are a Dictionary
        assert isinstance(config, dict), (
            "YAML file '%s' is not a dictionary" % path)
        return config

    @staticmethod
    def write_yaml(path: str, config: dict) -> None:
        yaml_file = open(path, "w+")
        yaml.dump(
            config,
            yaml_file,
            sort_keys=False,
            default_flow_style=None,
            allow_unicode=True,
        )

    """
    ConfigParser():
        - will take a config file path or a config and return a ClearpathConfig
    """

    def __new__(self, config):
        # Path: if config is path to config file, read YAML
        if isinstance(config, str):
            config = self.read_yaml(config)
        # Dict: if not path, it must be of type config
        assert isinstance(config, dict), "Configuration must be of type 'dict'"
        # ClearpathConfig
        cprconfig = ClearpathConfig()
        # SystemConfig
        cprconfig.system = SystemConfigParser(config)
        # PlatformConfig
        cprconfig.platform = PlatformConfigParser(config)
        # MountConfig
        cprconfig.mounts = MountsConfigParser(config)
        # SensorConfig
        cprconfig.sensors = SensorConfigParser(config)
        return cprconfig

#!/usr/bin/env python3

#------------------------------------------------------------------------------
#                 ODmeter - camera module
#
# Copyright (c) 2018 by Chang Liu.
# All rights reserved.

#------------------------------------------------------------------------------


from pyueye import ueye
import ctypes
from pyueye_example_utils import (uEyeException, Rect, get_bits_per_pixel,
                                  ImageBuffer, check)


#global variant
#TriggerMode = 2
BUFFER_COUNTS = 3

class Camera:
    def __init__(self, device_id=0):
        self.h_cam = ueye.HIDS(device_id)
        self.h_wnd = ueye.HWND()
        self.img_buffers = []

        # indicator for live mode
        self.live_on = False
        # trigger counter
        self.trigger_events = 0

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, _type, value, traceback):
        self.exit()

    def handle(self):
        return self.h_cam

    def alloc(self, buffer_count = BUFFER_COUNTS):
        rect = self.get_aoi()
        bpp = get_bits_per_pixel(self.get_colormode())

        self.free_image_memory()

        for i in range(buffer_count):
            buff = ImageBuffer()
            ueye.is_AllocImageMem(self.h_cam,
                                  rect.width, rect.height, bpp,
                                  buff.mem_ptr, buff.mem_id)

            check(ueye.is_AddToSequence(self.h_cam, buff.mem_ptr, buff.mem_id))
            self.img_buffers.append(buff)

        ueye.is_InitImageQueue(self.h_cam, 0)

    def free_image_memory(self):
        if self.live_on is True:
            self.stop_video()

        for buff in self.img_buffers:
            ret = ueye.is_FreeImageMem(self.h_cam, buff.mem_ptr, buff.mem_id)

            if ret != ueye.IS_SUCCESS:
                print("Free Image Memory Error!")
        # reset img_buffers
        self.img_buffers = []

    def init(self):
        ret = ueye.is_InitCamera(self.h_cam, self.h_wnd)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        self.enable_message(self.h_wnd)
        return ret

    def exit(self):
        ret = None
        if self.h_cam is not None:
            ret = ueye.is_ExitCamera(self.h_cam)

            #disable message by using None at the window
            self.enable_message(None)
        if ret == ueye.IS_SUCCESS:
            self.h_cam = None

    def get_aoi(self):
        rect_aoi = ueye.IS_RECT()
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

        return Rect(rect_aoi.s32X.value,
                    rect_aoi.s32Y.value,
                    rect_aoi.s32Width.value,
                    rect_aoi.s32Height.value)

    def set_aoi(self, x, y, width, height):
        if self.live_on is True:
            self.stop_video()

        print("stop video")
        rect_aoi = ueye.IS_RECT()
        rect_aoi.s32X = ueye.int(x)
        rect_aoi.s32Y = ueye.int(y)
        rect_aoi.s32Width = ueye.int(width)
        rect_aoi.s32Height = ueye.int(height)

        ret = ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

        self.alloc()
        self.capture_video()

        return None

    def capture_video(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        self.live_on = True
        return ueye.is_CaptureVideo(self.h_cam, wait_param)

    def stop_video(self):
        return ueye.is_StopLiveVideo(self.h_cam, ueye.IS_FORCE_VIDEO_STOP)

    def freeze_video(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        self.live_on = False
        return ueye.is_FreezeVideo(self.h_cam, wait_param)

    def set_colormode(self, colormode):
        check(ueye.is_SetColorMode(self.h_cam, colormode))

    def get_colormode(self):
        ret = ueye.is_SetColorMode(self.h_cam, ueye.IS_GET_COLOR_MODE)
        return ret

    def get_format_list(self):
        count = ueye.UINT()
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_NUM_ENTRIES, count, ueye.sizeof(count)))
        format_list = ueye.IMAGE_FORMAT_LIST(ueye.IMAGE_FORMAT_INFO * count.value)
        format_list.nSizeOfListEntry = ueye.sizeof(ueye.IMAGE_FORMAT_INFO)
        format_list.nNumListElements = count.value
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_LIST,
                                  format_list, ueye.sizeof(format_list)))
        return format_list

    def set_trigger_mode(self, TriggerMode):
        # Trigger off
        if TriggerMode == 0:
            ueye.is_SetExternalTrigger(self.h_cam, ueye.IS_SET_TRIGGER_OFF)
        # Software trigger
        elif TriggerMode == 1:
            ueye.is_SetExternalTrigger(self.h_cam, ueye.IS_SET_TRIGGER_SOFTWARE)
        # Hardware trigger falling edge
        elif TriggerMode == 2:
            ueye.is_SetExternalTrigger(self.h_cam, ueye.IS_SET_TRIGGER_HI_LO)
        # Hardware trigger rising edge
        elif TriggerMode == 3:
            ueye.is_SetExternalTrigger(self.h_cam, ueye.IS_SET_TRIGGER_LO_HI)

    def trigger_on(self, TriggerMode):
        # if live mode is on, stop the camera immediately
        if self.live_on is True:
            self.stop_video()

        # set the trigger and wait for the image
        self.set_trigger_mode(TriggerMode)
        # set the camera back to live mode

        self.capture_video()

    def enable_message(self, hwnd):
        ueye.is_EnableMessage(self.h_cam, ueye.IS_DEVICE_REMOVED, hwnd)

        ueye.is_EnableMessage(self.h_cam, ueye.IS_FRAME, hwnd)

        return ueye.is_EnableMessage(self.h_cam, ueye.IS_TRIGGER, hwnd)

    def get_frame_rate(self):
        framerate = ueye.c_double()
        ret = ueye.is_GetFramesPerSecond(self.h_cam, framerate)
        if ret == ueye.IS_SUCCESS:
            return framerate
        else:
            print("Get Frame Rate Error!")

    def get_pixel_clock_rate(self):
        command = ueye.IS_PIXELCLOCK_CMD_GET
        rate = ueye.uint(0)
        rate_size = ueye.sizeof(rate)
        ret = ueye.is_PixelClock(self.h_cam, command, rate, rate_size)
        if ret == ueye.IS_SUCCESS:
            return rate
        else:
            print("Get Pixel Clock Range Error")

    def get_pixel_clock_range(self):
        command = ueye.IS_PIXELCLOCK_CMD_GET_RANGE
        range = (ctypes.c_uint * 3)()
        range_size = 3 * ueye.sizeof(ueye.c_uint(0))
        ret = ueye.is_PixelClock(self.h_cam, command, range, range_size)
        if ret == ueye.IS_SUCCESS:
            print(range[1])
            return range[0], range[1]
        else:
            print("Get Pixel Clock Range Error")

    def get_sensor_info(self):
        sensor_info = ueye.SENSORINFO()
        ret = ueye.is_GetSensorInfo(self.h_cam, sensor_info)
        if ret == ueye.IS_SUCCESS:
            return sensor_info
        else:
            print("Get Sensor Info Error")

    def get_cam_info(self):
        cam_info = ueye.CAMINFO()
        ret = ueye.is_GetCameraInfo(self.h_cam, cam_info)
        if ret == ueye.IS_SUCCESS:
            return cam_info
        else:
            print("Get Camera Info Error")















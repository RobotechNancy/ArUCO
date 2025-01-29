import cv2
import pickle
import cv2.aruco as ar

from typing import Optional
from cv2.typing import MatLike


# Check centre cohérent avec les 4 coins
# Check theta z avec des codes autour du robot

class Camera:
    def __init__(self, calibration_file: Optional[str] = None):
        self.cap = cv2.VideoCapture(0)

        self.detector = ar.ArucoDetector(
            ar.getPredefinedDictionary(ar.DICT_4X4_1000),
            ar.DetectorParameters()
        )

        self.params: Optional[dict[str, MatLike]] = None
        if calibration_file:
            with open(calibration_file, "rb") as file:
                self.params = pickle.load(file)

    def calibrate(
        self, save_path: str, minimum_squares: int,
        capture_count: int, rows: int, columns: int,
        aruco_dict: int, square_length: float, markerLength: float
    ):
        predefined_dict = ar.getPredefinedDictionary(aruco_dict)

        board = ar.CharucoBoard(
            (columns, rows),
            squareLength=0.04,
            markerLength=0.03,
            dictionary=predefined_dict
        )

        valid_captures = 0
        ids_all: list[MatLike] = []
        corners_all: list[MatLike] = []

        print('Capturing frames...')

        while True:
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Can't receive frame")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = ar.detectMarkers(
                image=gray,
                dictionary=predefined_dict
            )

            if ids is None:
                continue

            response, charuco_corners, charuco_ids = ar.interpolateCornersCharuco(
                markerCorners=corners,
                markerIds=ids,
                image=gray,
                board=board
            )

            if response < minimum_squares:
                continue

            corners_all.append(charuco_corners)
            ids_all.append(charuco_ids)

            valid_captures += 1
            if valid_captures >= capture_count:
                break

        print('Generating calibration...')

        _, camera_matrix, dist_coeffs, _, _ = ar.calibrateCameraCharuco( # type: ignore
            corners_all, ids_all,
            board, gray.shape[::-1],
            None, None, # type: ignore
        )

        print('Saving calibration...')

        self.params = {
            "matrix": camera_matrix,
            "coeffs": dist_coeffs
        }

        with open(save_path, "wb") as file:
            pickle.dump(self.params, file)

        print('Done')

    def estimate(self, marker_length: float) -> Optional[tuple[MatLike, MatLike]]:
        if self.params is None:
            raise Exception("Can't use estimation without calibration")

        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Can't receive frame")

        corners, ids, _ = self.detector.detectMarkers(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        )

        if ids is None:
            return None

        rvecs, tvecs, _ = ar.estimatePoseSingleMarkers(
            corners,
            marker_length,
            self.params['matrix'],
            self.params['coeffs']
        )

        return tvecs, rvecs

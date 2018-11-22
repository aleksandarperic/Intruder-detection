import numpy as np
import cv2

# ============================================================================

CANVAS_SIZE = (600,800)

FINAL_LINE_COLOR = (255, 255, 255)
WORKING_LINE_COLOR = (0, 0, 255)

# ============================================================================

class PolygonDrawer(object):
    def __init__(self, window_name, img):
        self.window_name = window_name # Name for our window
        self.img = img

        self.done = False # Flag signalling we're done
        self.current = (0, 0) # Current position, so we can draw the line-in-progress
        self.points = [] # List of points defining our polygon


    def on_mouse(self, event, x, y, buttons, user_param):
        # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)

        if self.done: # Nothing more to do
            return

        if event == cv2.EVENT_MOUSEMOVE:
            # We want to be able to draw the line-in-progress, so update current mouse position
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            # Left click means adding a point at current position to the list of points
            print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
            self.points.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click means we're done
            print("Completing polygon with %d points." % len(self.points))
            self.done = True


    def runInitial(self):
        # Let's create our working window and set a mouse callback to handle events
        cv2.namedWindow(self.window_name)
        if (self.img is None):
            img = cv2.imread("coke.jpg")
        else:
            img = self.img
        cv2.imshow(self.window_name, img)
        cv2.waitKey(1)
        cv2.setMouseCallback(self.window_name, self.on_mouse)


        while(not self.done):
            # This is our drawing loop, we just continuously draw new images
            # and show them in the named window
            tmp_img = img
            if (len(self.points) > 0):
                # Draw all the current polygon segments
                cv2.polylines(tmp_img, np.array([self.points]), False, WORKING_LINE_COLOR, 1)
                # And  also show what the current segment would look like
                #cv2.line(tmp_img2, self.points[-1], self.current, WORKING_LINE_COLOR)
            # Update the window
            cv2.imshow(self.window_name, tmp_img)
            # And wait 50ms before next iteration (this will pump window messages meanwhile)
            if cv2.waitKey(50) == 27: # ESC hit
                self.done = True

        # User finised entering the polygon points, so let's make the final drawing
        stencil = np.zeros(img.shape).astype(img.dtype)
        # of a filled polygon
        if (len(self.points) > 0):
            cv2.fillPoly(stencil, np.array([self.points]), FINAL_LINE_COLOR)
        result = cv2.bitwise_and(img, stencil)
        # And show it
        cv2.imshow(self.window_name, result)
        # Waiting for the user to press any key
        cv2.waitKey()

        cv2.destroyWindow(self.window_name)
        return result

    def runContinue(self):
        if (self.img is None):
            img = cv2.imread("coke.jpg")
        else:
            img = self.img
        stencil = np.zeros(img.shape).astype(img.dtype)
        # of a filled polygon
        if (len(self.points) > 0):
            cv2.fillPoly(stencil, np.array([self.points]), FINAL_LINE_COLOR)
        result = cv2.bitwise_and(img, stencil)
        return result

# ============================================================================

if __name__ == "__main__":
    snapshot = cv2.imread("pepsi.png")
    pd = PolygonDrawer("Polygon", snapshot)
    image = pd.runInitial()
    cv2.imwrite("polygon.png", image)
    print("Polygon = %s" % pd.points)
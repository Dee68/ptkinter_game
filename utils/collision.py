def check_collision(a_bbox, b_bbox):
    """
    Check whether two axis-aligned bounding boxes (AABB) intersect.

    Each bounding box is expected to be in the format:
        [x1, y1, x2, y2]
    where (x1, y1) is the top-left corner and (x2, y2) is the bottom-right corner.

    The function determines collision by checking whether the rectangles
    overlap on both the x-axis and y-axis.

    Args:
        a_bbox (list[float]): Bounding box of object A.
        b_bbox (list[float]): Bounding box of object B.

    Returns:
        bool:
            True if the bounding boxes intersect (collision detected),
            False if they do not overlap or if either input is invalid.
    """
    
    if len(a_bbox) != 4 or len(b_bbox) != 4:
        return False

    ax1, ay1, ax2, ay2 = a_bbox
    bx1, by1, bx2, by2 = b_bbox

    return (
        ax1 < bx2 and
        ax2 > bx1 and
        ay1 < by2 and
        ay2 > by1
    )
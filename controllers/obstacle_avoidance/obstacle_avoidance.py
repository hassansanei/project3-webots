from controller import Robot

# =========================================================
# PROJECT 6 - Obstacle Avoidance
# Subsumption + Recovery + Hysteresis
# =========================================================

robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

# =========================================================
# Motors
# =========================================================

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")

left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# =========================================================
# Proximity Sensors
# =========================================================

ps = []

for i in range(8):
    sensor = robot.getDevice("ps" + str(i))
    sensor.enable(TIME_STEP)
    ps.append(sensor)

# =========================================================
# Parameters
# =========================================================

MAX_SPEED = 6.28

FORWARD_SPEED = 2.8

TURN_SPEED = 3.2

BACK_SPEED = 2.0

# شروع تشخیص مانع
OBSTACLE_THRESHOLD = 500

# مانع خیلی نزدیک
DANGER_THRESHOLD = 1200

# برای خروج از حالت مانع
CLEAR_THRESHOLD = 350

# مدت زمان چرخش اجباری
TURN_STEPS = 20

# مدت عقب رفتن
BACK_STEPS = 12

# =========================================================
# State
# =========================================================

MODE_FORWARD = 0
MODE_TURN = 1
MODE_BACK = 2

mode = MODE_FORWARD

turn_direction = 0
timer = 0


# =========================================================
# Helper
# =========================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


# =========================================================
# Main Loop
# =========================================================

while robot.step(TIME_STEP) != -1:

    # -----------------------------------------------------
    # Read all sensors
    # -----------------------------------------------------

    v = [sensor.getValue() for sensor in ps]

    ps0 = v[0]
    ps1 = v[1]
    ps2 = v[2]
    ps3 = v[3]
    ps4 = v[4]
    ps5 = v[5]
    ps6 = v[6]
    ps7 = v[7]

    # -----------------------------------------------------
    # Sensor grouping
    #
    # Standard e-puck:
    #
    #       ps7   ps0
    #     ps6       ps1
    #     ps5       ps2
    #       ps4   ps3
    #
    # -----------------------------------------------------

    front = max(ps0, ps7)

    front_right = max(ps1, ps2)

    front_left = max(ps6, ps5)

    right_side = ps2

    left_side = ps5

    # -----------------------------------------------------
    # Print
    # -----------------------------------------------------

    print(
        f"0={ps0:6.1f} "
        f"1={ps1:6.1f} "
        f"2={ps2:6.1f} "
        f"3={ps3:6.1f} "
        f"4={ps4:6.1f} "
        f"5={ps5:6.1f} "
        f"6={ps6:6.1f} "
        f"7={ps7:6.1f} "
        f"| F={front:6.1f} "
        f"FL={front_left:6.1f} "
        f"FR={front_right:6.1f}"
    )

    # =====================================================
    # MODE 2 : BACK
    # =====================================================

    if mode == MODE_BACK:

        left_speed = -BACK_SPEED
        right_speed = -BACK_SPEED

        timer -= 1

        if timer <= 0:

            mode = MODE_TURN
            timer = TURN_STEPS

            # انتخاب جهت بر اساس فضای آزادتر
            if front_left < front_right:
                turn_direction = -1
            else:
                turn_direction = 1

        print("MODE: BACK")

    # =====================================================
    # MODE 1 : TURN
    # =====================================================

    elif mode == MODE_TURN:

        timer -= 1

        if turn_direction == -1:

            # چرخش به چپ
            left_speed = -TURN_SPEED
            right_speed = TURN_SPEED

            print("MODE: TURN LEFT")

        else:

            # چرخش به راست
            left_speed = TURN_SPEED
            right_speed = -TURN_SPEED
            print("MODE: TURN RIGHT")

        # -------------------------------------------------
        # بعد از حداقل زمان چرخش،
        # اگر جلوی ربات آزاد شد، حرکت کن
        # -------------------------------------------------

        if timer <= 0:

            if front < CLEAR_THRESHOLD:

                mode = MODE_FORWARD

            else:

                # هنوز مانع وجود دارد
                # دوباره چند قدم بچرخ
                timer = TURN_STEPS

    # =====================================================
    # MODE 0 : FORWARD
    # =====================================================

    else:

        # -------------------------------------------------
        # خطر خیلی نزدیک
        # -------------------------------------------------

        if front >= DANGER_THRESHOLD:

            mode = MODE_BACK

            timer = BACK_STEPS

            print("!!! DANGER -> BACK")

            left_speed = -BACK_SPEED
            right_speed = -BACK_SPEED

        # -------------------------------------------------
        # مانع در جلو
        # -------------------------------------------------

        elif front >= OBSTACLE_THRESHOLD:

            # فضای سمت چپ و راست را مقایسه می‌کنیم

            if front_left < front_right:

                # چپ آزادتر است
                turn_direction = -1

            else:

                # راست آزادتر است
                turn_direction = 1

            mode = MODE_TURN
            timer = TURN_STEPS

            if turn_direction == -1:

                left_speed = -TURN_SPEED
                right_speed = TURN_SPEED

                print("FRONT OBSTACLE -> TURN LEFT")

            else:

                left_speed = TURN_SPEED
                right_speed = -TURN_SPEED

                print("FRONT OBSTACLE -> TURN RIGHT")

        # -------------------------------------------------
        # مانع در سمت راست
        # -------------------------------------------------

        elif right_side >= OBSTACLE_THRESHOLD:

            # مانع راست → کمی به چپ

            left_speed = FORWARD_SPEED * 0.45
            right_speed = FORWARD_SPEED

            print("RIGHT OBSTACLE -> STEER LEFT")

        # -------------------------------------------------
        # مانع در سمت چپ
        # -------------------------------------------------

        elif left_side >= OBSTACLE_THRESHOLD:

            # مانع چپ → کمی به راست

            left_speed = FORWARD_SPEED
            right_speed = FORWARD_SPEED * 0.45

            print("LEFT OBSTACLE -> STEER RIGHT")

        # -------------------------------------------------
        # هیچ مانعی نیست
        # -------------------------------------------------

        else:

            left_speed = FORWARD_SPEED
            right_speed = FORWARD_SPEED

            print("FORWARD")

    # =====================================================
    # Limit speed
    # =====================================================

    left_speed = clamp(
        left_speed,
        -MAX_SPEED,
        MAX_SPEED
    )

    right_speed = clamp(
        right_speed,
        -MAX_SPEED,
        MAX_SPEED
    )

    # =====================================================
    # Motors
    # =====================================================

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
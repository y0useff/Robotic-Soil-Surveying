
import math
import serial.tools.list_ports
import time

# !/usr/bin/env python3

class HuskyBaseController:
    def __init__(self):
        # Initialize ROS node
        rospy.init_node('husky_base_controller')
        
        # MOVEMENT SETTINGS - Adjust these values
        self.default_speed = 0.1        # Default speed in m/s (0.05 = very slow, 0.2 = moderate, 0.5 = fast)
        self.default_distance = 0.3     # Default distance in meters
        
        # Publisher for base velocity commands
        self.cmd_vel_pub = rospy.Publisher('/husky_velocity_controller/cmd_vel', 
                                          Twist, queue_size=1)
        
        # Subscriber for odometry to track distance
        self.odom_sub = rospy.Subscriber('/odometry/filtered', Odometry, 
                                        self.odom_callback)
        
        # Initialize odometry tracking
        self.start_position = None
        self.current_position = None
        
        rospy.loginfo("Husky Base Controller initialized")
        rospy.loginfo("Default settings - Speed: {} m/s, Distance: {} m".format(
            self.default_speed, self.default_distance))
        

    ############I DO NOT KNOW IF THIS WORKS. AI GENERATED. TEST TOMORROW
    def turn_in_place(self, angle_rad, angular_speed=0.3):
        """
        Turn the robot in place by a given angle (in radians)
        Positive angle: left turn, Negative angle: right turn

        Args:
            angle_rad (float): Angle to turn (in radians)
            angular_speed (float): Speed in rad/s
        """
        rospy.loginfo("=" * 50)
        direction = "left" if angle_rad > 0 else "right"
        rospy.loginfo(f"Turning {direction} {abs(angle_rad):.2f} radians at {angular_speed:.2f} rad/s")

        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = angular_speed if angle_rad > 0 else -angular_speed

        rate = rospy.Rate(10)  # 10 Hz
        duration = abs(angle_rad) / angular_speed
        start_time = rospy.Time.now()

        while not rospy.is_shutdown():
            elapsed = (rospy.Time.now() - start_time).to_sec()
            if elapsed >= duration:
                break
            self.cmd_vel_pub.publish(twist)
            rate.sleep()

        # Stop rotation
        stop_twist = Twist()
        for _ in range(10):
            self.cmd_vel_pub.publish(stop_twist)
            rospy.sleep(0.1)

        rospy.loginfo("Turn complete")
        rospy.loginfo("=" * 50)
        ############I DO NOT KNOW IF THIS WORKS. AI GENERATED. TEST TOMORROW

    
    def odom_callback(self, msg):
        """Callback to track robot position from odometry"""
        self.current_position = msg.pose.pose.position
        
        if self.start_position is None:
            self.start_position = msg.pose.pose.position
            rospy.loginfo("Start position recorded: x={:.3f}, y={:.3f}".format(
                self.start_position.x, self.start_position.y))
    
    def move_base(self, distance=None, speed=None):
        """
        Move the base forward (positive distance) or backward (negative distance)
        
        Args:
            distance: Distance to move in meters (positive=forward, negative=backward)
                     If None, uses self.default_distance
            speed: Speed in m/s (always positive)
                   If None, uses self.default_speed
        """
        # Use defaults if not specified
        if distance is None:
            distance = self.default_distance
        if speed is None:
            speed = self.default_speed
            
        direction = "forward" if distance > 0 else "backward"
        rospy.loginfo("=" * 50)
        rospy.loginfo("Moving {} {:.3f}m at {:.3f}m/s...".format(
            direction, abs(distance), speed))
        
        # Wait for odometry to initialize
        rate = rospy.Rate(10)  # 10 Hz
        timeout = 5.0  # 5 second timeout
        start_wait = rospy.Time.now()
        
        while self.current_position is None and not rospy.is_shutdown():
            if (rospy.Time.now() - start_wait).to_sec() > timeout:
                rospy.logerr("Timeout waiting for odometry data!")
                return False
            rospy.logwarn("Waiting for odometry data...")
            rate.sleep()
        
        # Reset start position for this movement
        self.start_position = self.current_position
        
        # Create velocity command
        twist = Twist()
        twist.linear.x = speed if distance > 0 else -speed  # Negative for backward
        twist.angular.z = 0.0   # No rotation
        
        # Move until distance is reached
        while not rospy.is_shutdown():
            if self.current_position is not None:
                # Calculate distance traveled
                dx = self.current_position.x - self.start_position.x
                dy = self.current_position.y - self.start_position.y
                distance_traveled = math.sqrt(dx**2 + dy**2)
                
                # Progress bar visualization
                progress = distance_traveled / abs(distance)
                bar_length = 30
                filled_length = int(bar_length * progress)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                
                # Print progress
                print("\rProgress: [{0}] {1:.1f}% ({2:.3f}m / {3:.3f}m)".format(
                    bar, progress * 100, distance_traveled, abs(distance)), end='')
                
                if distance_traveled >= abs(distance):
                    # Stop the robot
                    twist.linear.x = 0.0
                    self.cmd_vel_pub.publish(twist)
                    print()  # New line after progress bar
                    rospy.loginfo("Movement complete! Traveled {:.3f}m".format(distance_traveled))
                    break
                else:
                    # Continue moving
                    self.cmd_vel_pub.publish(twist)
            
            rate.sleep()
        
        # Ensure robot is stopped
        stop_twist = Twist()
        for _ in range(10):  # Publish stop command multiple times
            self.cmd_vel_pub.publish(stop_twist)
            rospy.sleep(0.1)
            
        rospy.loginfo("=" * 50)
        return True
    
    def move_forward(self, distance=None, speed=None):
        """Convenience method to move forward"""
        if distance is None:
            distance = self.default_distance
        return self.move_base(abs(distance), speed)
    
    def move_backward(self, distance=None, speed=None):
        """Convenience method to move backward"""
        if distance is None:
            distance = self.default_distance
        return self.move_base(-abs(distance), speed)
    
    def stop(self):
        """Emergency stop"""
        stop_twist = Twist()
        for _ in range(20):
            self.cmd_vel_pub.publish(stop_twist)
            rospy.sleep(0.05)
        rospy.loginfo("Robot stopped!")


# #Establish communication W husky

# #Establish communication W/ Arduino

# Create controller
# controller = HuskyBaseController()

# # Give system time to initialize
# rospy.sleep(1.0)

# #ensure motor is retracted
# serialInst.write(b'OFF8\n')
# serialInst.write(b'ON7\n')
# time.sleep(20)


# # Example usage - modify as needed:

# controller.move_forward(distance=1.83, speed=0.15) #move 1.83 meters (6 feet to edge of plot)
# rospy.sleep(1)
# controller.move_forward(distance=0.5, speed=0.15) #move 0.5 meters into aisle of plot (1.6 feet)
# rospy.sleep(1)
# # Turn 90 degrees left onto plot (π/2 radians)
# controller.turn_in_place(angle_rad=math.pi/2, angular_speed=0.5)
# rospy.sleep(1)

# samples = 0

try:
    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    portsList = []

    for onePort in ports:
        portsList.append(str(onePort))
        print(str(onePort))

    val = input("Select Port:")

    application = input("What application group is this: ")
    plot_number = input("What plot number is this: ")

    for x in range(0,len(portsList)):
        # if portsList[x].startswith("COM" + str(val)):
        portVar = str(val)
        print(portVar)

    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()
    time.sleep(3)
    ###EXTENDS MOTOR DOWNWARDS
    serialInst.write(b'ON8\n')
    serialInst.write(b'OFF7\n')
    time.sleep(20)
    serialInst.write(b'OFF8\n')
    serialInst.write(b'OFF7\n')
    start_time = time.time()
    duration = 90  # seconds

    while time.time() - start_time < duration:
        if serialInst.in_waiting:
            packet = serialInst.readline()
            decoded_packet = packet.decode('utf-8').rstrip('\n') #read packet coming from serial monitor
            with open(f"{application}-{plot_number}", "a") as file:
                # Wçrite the packet to the text file
                file.write(f"{decoded_packet}\n")

    time.sleep(20)

    serialInst.write(b'ON7\n')
    serialInst.write(b'OFF8\n')
    time.sleep(20)
    serialInst.write(b'OFF7\n')
    serialInst.write(b'OFF8\n')
except:
    serialInst.write(b'ON7\n')
    serialInst.write(b'OFF8\n')
    time.sleep(20)
    serialInst.write(b'OFF7\n')
    serialInst.write(b'OFF8\n')


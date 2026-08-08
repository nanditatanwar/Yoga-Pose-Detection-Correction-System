from utils.angles import calculate_angle, calculate_distance


class PoseAnalyzer:
    def __init__(self):
        self.landmarks = {}

    def set_landmarks(self, landmarks):
        self.landmarks = landmarks

    def get_landmark(self, name, default=(0, 0, 0)):
        """Safely get a landmark"""
        return self.landmarks.get(name, default)

    def has_required_landmarks(self, pose_name):
        """Check required landmarks for a pose"""
        basic_landmarks = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']

        pose_requirements = {
            'tadasana': basic_landmarks + ['left_ankle', 'right_ankle', 'left_wrist', 'right_wrist', 'nose'],
            'vriksasana': basic_landmarks + ['left_ankle', 'right_ankle'],
            'padahastasana': basic_landmarks + ['left_knee', 'left_ankle'],
            'ardha_chakrasana': basic_landmarks + ['left_wrist', 'right_wrist', 'left_knee', 'right_knee', 'nose'],
            'trikonasana': basic_landmarks + ['left_ankle', 'right_ankle', 'left_wrist', 'right_wrist', 'left_knee', 'right_knee'],
            'bhadrasana': basic_landmarks + ['left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'nose', 'left_wrist', 'right_wrist'],
            'vajrasana': basic_landmarks + ['left_knee', 'right_knee'],
            'ustrasana': basic_landmarks + ['left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'left_wrist', 'right_wrist', 'left_heel', 'right_heel'],
            'sasakasana': basic_landmarks + ['left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'left_wrist', 'right_wrist', 'left_heel', 'right_heel', 'nose']
        }

        required = pose_requirements.get(pose_name, basic_landmarks)
        missing = [lm for lm in required if lm not in self.landmarks]

        if missing:
            print(f"DEBUG: Missing landmarks for {pose_name}: {missing}")
            return False, missing
        return True, []

    # -------------------------
    # Helper: Score & feedback
    # -------------------------
    def safe_feedback(self, feedback_list, condition, msg_fail, msg_pass=None, score_subtract=0):
        if not condition:
            feedback_list.append(msg_fail)
            return score_subtract
        elif msg_pass:
            feedback_list.append(msg_pass)
        return 0

    # -------------------------
    # Individual Pose Analyzers
    # -------------------------
    def analyze_tadasana(self):
        feedback = []
        score = 100
        lm = self.landmarks

        has_enough, missing = self.has_required_landmarks('tadasana')
        if not has_enough:
            feedback.append(f"Ensure full body is visible: missing {', '.join(missing)}")
            return feedback, 50

        avg_wrist_y = (self.get_landmark('left_wrist')[1] + self.get_landmark('right_wrist')[1]) / 2
        avg_hip_y = (self.get_landmark('left_hip')[1] + self.get_landmark('right_hip')[1]) / 2
        score -= self.safe_feedback(feedback, avg_wrist_y > avg_hip_y, "Lower your arms by your sides", "✓ Arms down", 40)

        shoulder_diff = abs(self.get_landmark('left_shoulder')[1] - self.get_landmark('right_shoulder')[1])
        score -= self.safe_feedback(feedback, shoulder_diff <= 0.05, "Level your shoulders", "✓ Shoulders level", 15)

        hip_diff = abs(self.get_landmark('left_hip')[1] - self.get_landmark('right_hip')[1])
        score -= self.safe_feedback(feedback, hip_diff <= 0.05, "Align hips evenly", "✓ Hips aligned", 15)

        mid_hip_x = (self.get_landmark('left_hip')[0] + self.get_landmark('right_hip')[0]) / 2
        head_offset = abs(self.get_landmark('nose')[0] - mid_hip_x)
        score -= self.safe_feedback(feedback, head_offset <= 0.12, "Align head over body", "✓ Head aligned", 15)

        mid_ankle_x = (self.get_landmark('left_ankle')[0] + self.get_landmark('right_ankle')[0]) / 2
        score -= self.safe_feedback(feedback, abs(mid_ankle_x - mid_hip_x) <= 0.1, "Distribute weight evenly", "✓ Weight centered", 10)

        score = max(score, 0)
        if score >= 85:
            feedback.append("✓ Correct Tadasana")
        elif score >= 65:
            feedback.append("Almost correct, refine posture")
        else:
            feedback.append("Not Tadasana posture")
        return feedback, score

    def analyze_vriksasana(self):
        feedback = []
        score = 100
        has_enough, missing = self.has_required_landmarks('vriksasana')
        if not has_enough:
            feedback.append(f"Make sure your {', '.join(missing)} are visible")
            return feedback, 50

        la = self.get_landmark('left_ankle')
        ra = self.get_landmark('right_ankle')
        height_diff = abs(la[1] - ra[1])
        if height_diff < 0.1:
            feedback.append("Lift one foot to inner thigh")
            score -= 30
        elif height_diff > 0.2:
            feedback.append("✓ Vriksasana")
        else:
            feedback.append("Maintain balance")
        return feedback, max(score, 0)

    def analyze_padahastasana(self):
        feedback = []
        score = 100
        has_enough, missing = self.has_required_landmarks('padahastasana')
        if not has_enough:
            feedback.append(f"Make sure your {', '.join(missing)} are visible")
            return feedback, 50

        ls = self.get_landmark('left_shoulder')
        lh = self.get_landmark('left_hip')
        score -= self.safe_feedback(feedback, ls[1] < lh[1] + 0.1, "Bend forward more from hips", "✓ Padahastasana", 30)
        return feedback, max(score, 0)

    def analyze_ardha_chakrasana(self):
        feedback = []
        score = 100
        has_enough, missing = self.has_required_landmarks('ardha_chakrasana')
        if not has_enough:
            feedback.append(f"Make sure your {', '.join(missing)} are visible")
            return feedback, 50

        # Back bend check
        shoulder_x = self.get_landmark('left_shoulder')[0]
        hip_x = self.get_landmark('left_hip')[0]
        score -= self.safe_feedback(feedback, shoulder_x < hip_x - 0.05, "Lean back more - shoulders behind hips", "✓ Ardha Chakrasana", 25)

        # Hands on hips
        wrist = self.get_landmark('left_wrist')
        distance = abs(wrist[0] - hip_x) + abs(wrist[1] - self.get_landmark('left_hip')[1])
        score -= self.safe_feedback(feedback, distance <= 0.15, "Place hands firmly on hips", "✓ Hands on hips", 20)

        # Knee straight
        knee_angle = calculate_angle(self.get_landmark('left_hip'), self.get_landmark('left_knee'), self.get_landmark('left_ankle'))
        score -= self.safe_feedback(feedback, knee_angle >= 170, "Keep knees straight", "✓ Knees straight", 15)

        # Chest lifted
        nose_y = self.get_landmark('nose')[1]
        shoulder_y = self.get_landmark('left_shoulder')[1]
        score -= self.safe_feedback(feedback, nose_y <= shoulder_y, "Lift chest, look upward", "✓ Chest lifted", 15)

        score = max(score, 0)
        if score >= 85:
            feedback.append("✓ Correct Ardha Chakrasana")
        elif score >= 60:
            feedback.append("Almost correct, adjust posture")
        else:
            feedback.append("Not Ardha Chakrasana")
        return feedback, score

    def analyze_trikonasana(self):
        feedback = []
        score = 100
        has_enough, missing = self.has_required_landmarks('trikonasana')
        if not has_enough:
            feedback.append(f"Make sure your {', '.join(missing)} are visible")
            return feedback, 50

        # Stance width
        lh = self.get_landmark('left_hip')
        rh = self.get_landmark('right_hip')
        la = self.get_landmark('left_ankle')
        ra = self.get_landmark('right_ankle')
        stance_width = abs(la[0] - ra[0])
        hip_width = abs(lh[0] - rh[0])
        score -= self.safe_feedback(feedback, stance_width >= hip_width*1.8, "Widen your stance", "✓ Good wide stance", 20)

        # Arm reach
        lw = self.get_landmark('left_wrist')
        rw = self.get_landmark('right_wrist')
        active_wrist, active_ankle = (lw, la) if abs(lw[1]-la[1])<abs(rw[1]-ra[1]) else (rw, ra)
        score -= self.safe_feedback(feedback, calculate_distance(active_wrist, active_ankle) <= hip_width*1.2, "Reach hand toward ankle or shin", "✓ Good reach", 25)

        # Legs straight
        for side in ['left', 'right']:
            angle = calculate_angle(self.get_landmark(f'{side}_hip'), self.get_landmark(f'{side}_knee'), self.get_landmark(f'{side}_ankle'))
            score -= self.safe_feedback(feedback, angle >= 170, f"Straighten {side} leg", f"✓ {side} leg straight", 15)

        # Chest open
        ls = self.get_landmark('left_shoulder')
        rs = self.get_landmark('right_shoulder')
        score -= self.safe_feedback(feedback, abs(ls[1]-rs[1]) < hip_width*0.3, "Open chest and stack shoulders", "✓ Chest open", 15)

        score = max(score, 0)
        if score >= 85:
            feedback.append("✓ Correct Trikonasana")
        elif score >= 60:
            feedback.append("Almost correct, refine posture")
        else:
            feedback.append("Not Trikonasana posture")
        return feedback, score

    def analyze_bhadrasana(self):
        feedback = []
        score = 100
        has_enough, missing = self.has_required_landmarks('bhadrasana')
        if not has_enough:
            feedback.append(f"Make sure your {', '.join(missing)} are visible")
            return feedback, 50

        lh = self.get_landmark('left_hip')
        rh = self.get_landmark('right_hip')
        lk = self.get_landmark('left_knee')
        rk = self.get_landmark('right_knee')
        la = self.get_landmark('left_ankle')
        ra = self.get_landmark('right_ankle')
        nose = self.get_landmark('nose')
        lw = self.get_landmark('left_wrist')
        rw = self.get_landmark('right_wrist')
        mid_hip_x = (lh[0]+rh[0])/2
        hip_y = (lh[1]+rh[1])/2

        # Sitting posture
        knee_y_avg = (lk[1]+rk[1])/2
        score -= self.safe_feedback(feedback, hip_y >= knee_y_avg - 0.05, "Sit closer to the ground", "✓ Stable seated posture", 20)

        # Feet together
        ankle_x_dist = abs(la[0]-ra[0])
        score -= self.safe_feedback(feedback, ankle_x_dist <= 0.1, "Bring feet closer together", "✓ Feet together", 20)
        ankle_y_dist = abs(la[1]-ra[1])
        score -= self.safe_feedback(feedback, ankle_y_dist <= 0.05, "Align both feet at the same level", "✓ Feet aligned", 10)

        # Knees relaxed
        knee_opening = abs(lk[0]-rk[0])
        hip_width = abs(lh[0]-rh[0])
        score -= self.safe_feedback(feedback, knee_opening >= hip_width*0.9, "Relax knees outward", "✓ Knees opened comfortably", 20)

        # Spine straight
        score -= self.safe_feedback(feedback, abs(nose[0]-mid_hip_x)<=0.08, "Keep spine straight and upright", "✓ Upright spine", 15)

        # Hands optional
        left_hand_dist = calculate_distance(lw, la)
        right_hand_dist = calculate_distance(rw, ra)
        if left_hand_dist>0.25 and right_hand_dist>0.25:
            feedback.append("Optional: Hold feet for deeper stretch")
        else:
            feedback.append("✓ Hands placed well")

        score = max(score, 0)
        if score >= 85:
            feedback.append("✓ Correct Bhadrasana")
        elif score >= 60:
            feedback.append("Almost correct, refine posture")
        else:
            feedback.append("Not Bhadrasana posture")
        return feedback, score
        def analyze_vajrasana(self):
            """Analyze Vajrasana (Thunderbolt Pose)"""
            feedback = []
            score = 100
            has_enough, missing = self.has_required_landmarks('vajrasana')
            if not has_enough:
                feedback.append(f"Make sure your {', '.join(missing)} are visible")
                return feedback, 50

        # 1. Sitting low
            hip_y = self.get_landmark('left_hip')[1]
            if hip_y > 0.6:
                feedback.append("✓ Good sitting position")
            else:
                feedback.append("Sit lower, closer to ground")
                score -= 25

        # 2. Spine alignment
            shoulder_x = self.get_landmark('left_shoulder')[0]
            hip_x = self.get_landmark('left_hip')[0]
            if abs(shoulder_x - hip_x) < 0.1:
                feedback.append("✓ Spine aligned")
            else:
                feedback.append("Keep spine straight")
                score -= 25

        # 3. Knees bent
            knee_y = self.get_landmark('left_knee')[1]
            if knee_y > hip_y:
                feedback.append("✓ Knees properly bent")
            else:
                feedback.append("Bend knees more")
                score -= 25

        # 4. Shoulders level
            left_sh_y = self.get_landmark('left_shoulder')[1]
            right_sh_y = self.get_landmark('right_shoulder')[1]
            if abs(left_sh_y - right_sh_y) < 0.05:
                feedback.append("✓ Shoulders level")
            else:
                feedback.append("Level your shoulders")
                score -= 25

            score = max(score, 0)
            if score >= 85:
                feedback.append("✓ Correct Vajrasana")
            elif score >= 60:
                feedback.append("Almost correct, refine posture")
            else:
                feedback.append("Not Vajrasana posture")
            return feedback, score

    def analyze_ustrasana(self):
        """Analyze Ustrasana (Camel Pose) – SIDE VIEW"""
        feedback = []
        score = 100
        lm = self.landmarks

        required = ['left_shoulder','right_shoulder','left_hip','right_hip',
                    'left_knee','right_knee','left_ankle','right_ankle',
                    'left_wrist','right_wrist','left_heel','right_heel']
        missing = [k for k in required if k not in lm]
        if missing:
            feedback.append(f"Ensure full body is visible: missing {', '.join(missing)}")
            return feedback, 40

        # 0. SIDE VIEW
        side = 'left' if lm['left_shoulder'][2] < lm['right_shoulder'][2] else 'right'
        shoulder = self.get_landmark(f'{side}_shoulder')
        hip = self.get_landmark(f'{side}_hip')
        knee = self.get_landmark(f'{side}_knee')
        ankle = self.get_landmark(f'{side}_ankle')
        wrist = self.get_landmark(f'{side}_wrist')
        heel = self.get_landmark(f'{side}_heel')

        # 1. Kneeling check
        avg_knee_y = (self.get_landmark('left_knee')[1]+self.get_landmark('right_knee')[1])/2
        avg_hip_y = (self.get_landmark('left_hip')[1]+self.get_landmark('right_hip')[1])/2
        if avg_knee_y <= avg_hip_y:
            feedback.append("Kneel on the floor")
            score -= 30

        # 2. Back bend angle
        spine_angle = calculate_angle(knee, hip, shoulder)
        if spine_angle > 155:
            feedback.append("Increase back bend")
            score -= 30
        elif spine_angle > 140:
            feedback.append("Good back bend, go deeper")
            score -= 15
        else:
            feedback.append("✓ Strong back bend")

        # 3. Hand to heel
        leg_length = calculate_distance(hip, ankle)
        hand_dist = calculate_distance(wrist, heel)
        if hand_dist > leg_length*0.35:
            feedback.append("Bring hand to heel")
            score -= 20
        else:
            feedback.append("✓ Hand on heel")

        # 4. Hips forward
        hip_forward = hip[0] - knee[0]
        if hip_forward < 0.05:
            feedback.append("Push hips forward")
            score -= 20
        else:
            feedback.append("✓ Hips pushed forward")

        # 5. Thigh vertical
        if abs(hip[0]-knee[0]) > 0.1:
            feedback.append("Keep thigh vertical")
            score -= 10
        else:
            feedback.append("✓ Thigh vertical")

        score = max(score, 0)
        if score >= 80:
            feedback.append("✓ Correct Camel Pose")
        elif score >= 60:
            feedback.append("Almost correct, adjust posture")
        else:
            feedback.append("Not a correct Camel Pose")
        return feedback, score

    def analyze_sasakasana(self):
        """Analyze Sasakasana (Rabbit Pose) – seated, side view"""
        feedback = []
        score = 100
        lm = self.landmarks

        required = ['left_shoulder','right_shoulder','left_hip','right_hip',
                    'left_knee','right_knee','left_ankle','right_ankle',
                    'left_wrist','right_wrist','left_heel','right_heel','nose']
        missing = [k for k in required if k not in lm]
        if missing:
            feedback.append(f"Ensure full body is visible: missing {', '.join(missing)}")
            return feedback, 40

        # 1. Kneeling / seated
        hip_knee_angle_l = calculate_angle(lm['left_hip'], lm['left_knee'], lm['left_ankle'])
        hip_knee_angle_r = calculate_angle(lm['right_hip'], lm['right_knee'], lm['right_ankle'])
        avg_hip_knee_angle = (hip_knee_angle_l + hip_knee_angle_r)/2
        if avg_hip_knee_angle > 110:
            feedback.append("Sit back on your heels")
            score -= 25
        else:
            feedback.append("✓ Kneeling seated position")

        # 2. Spine flexion
        spine_l = calculate_angle(lm['left_knee'], lm['left_hip'], lm['left_shoulder'])
        spine_r = calculate_angle(lm['right_knee'], lm['right_hip'], lm['right_shoulder'])
        spine_angle = (spine_l + spine_r)/2
        if spine_angle > 150:
            feedback.append("Round your spine forward more")
            score -= 30
        elif spine_angle > 135:
            feedback.append("Good spinal flexion, go deeper")
            score -= 10
        else:
            feedback.append("✓ Deep spinal flexion")

        # 3. Head tuck
        avg_shoulder_y = (lm['left_shoulder'][1]+lm['right_shoulder'][1])/2
        if lm['nose'][1] < avg_shoulder_y:
            feedback.append("Tuck chin toward chest")
            score -= 15
        else:
            feedback.append("✓ Head tucked correctly")

        # 4. Hands holding heels
        leg_length = calculate_distance(lm['left_hip'], lm['left_ankle'])
        for side in ['left','right']:
            if calculate_distance(lm[f'{side}_wrist'], lm[f'{side}_heel']) > leg_length*0.35:
                feedback.append(f"Hold your {side} heel firmly")
                score -= 15

        # 5. Hips grounded
        avg_hip_y = (lm['left_hip'][1]+lm['right_hip'][1])/2
        avg_knee_y = (lm['left_knee'][1]+lm['right_knee'][1])/2
        if avg_hip_y < avg_knee_y - 0.05:
            feedback.append("Keep hips grounded on heels")
            score -= 15
        else:
            feedback.append("✓ Hips grounded")

        score = max(score, 0)
        if score >= 85:
            feedback.append("✓ Correct Sasakasana")
        elif score >= 60:
            feedback.append("Almost correct, refine posture")
        else:
            feedback.append("Not a correct Sasakasana")
        return feedback, score
    
    def analyze_pose(self, pose_name):
        if pose_name == 'tadasana':
            return self.analyze_tadasana()
        elif pose_name == 'vriksasana':
            return self.analyze_vriksasana()
        elif pose_name == 'padahastasana':
            return self.analyze_padahastasana()
        elif pose_name == 'ardha_chakrasana':
            return self.analyze_ardha_chakrasana()
        elif pose_name == 'trikonasana':
            return self.analyze_trikonasana()
        elif pose_name == 'bhadrasana': 
            return self.analyze_bhadrasana()
        elif pose_name == 'vajrasana':
            return self.analyze_vajrasana() 
        elif pose_name == 'sasakasana':
            return self.analyze_sasakasana()
        elif pose_name == 'ustrasana':
            return self.analyze_ustrasana()
        else:
            return [f"Practice {pose_name}"], 50


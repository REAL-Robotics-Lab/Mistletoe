# ------------ reward functions----------------
def _reward_lin_vel_z(self):
    # Penalize z axis base linear velocity
    return torch.square(self.base_lin_vel[:, 2])

def _reward_ang_vel_xy(self):
    # Penalize xy axes base angular velocity
    return torch.sum(torch.square(self.base_ang_vel[:, :2]), dim=1)

def _reward_orientation(self):
    # Penalize non flat base orientation
    return torch.sum(torch.square(self.projected_gravity[:, :2]), dim=1)

def _reward_base_height(self):
    # Penalize base height away from target
    base_height = torch.mean(self.root_states[:, 2].unsqueeze(1) - self.measured_heights, dim=1)
    return torch.square(base_height - self.cfg.rewards.base_height_target)

def _reward_torques(self):
    # Penalize torques
    return torch.sum(torch.square(self.torques), dim=1)

def _reward_energy(self):
    # Penalize torques
    return torch.sum(torch.multiply(self.torques, self.dof_vel), dim=1)

def _reward_energy_expenditure(self):
    # Penalize torques
    return torch.sum(torch.clip(torch.multiply(self.torques, self.dof_vel), 0, 1e30), dim=1)

def _reward_dof_vel(self):
    # Penalize dof velocities
    return torch.sum(torch.square(self.dof_vel), dim=1)

def _reward_dof_acc(self):
    # Penalize dof accelerations
    return torch.sum(torch.square((self.last_dof_vel - self.dof_vel) / self.dt), dim=1)

def _reward_action_rate(self):
    # Penalize changes in actions
    return torch.sum(torch.square(self.last_actions - self.actions), dim=1)

def _reward_collision(self):
    # Penalize collisions on selected bodies
    return torch.sum(1. * (torch.norm(self.contact_forces[:, self.penalised_contact_indices, :], dim=-1) > 0.1),
                        dim=1)

def _reward_termination(self):
    # Terminal reward / penalty
    return self.reset_buf * ~self.time_out_buf

def _reward_survival(self):
    # Survival reward / penalty
    return ~(self.reset_buf * ~self.time_out_buf)

def _reward_dof_pos_limits(self):
    # Penalize dof positions too close to the limit
    out_of_limits = -(self.dof_pos - self.dof_pos_limits[:, 0]).clip(max=0.)  # lower limit
    out_of_limits += (self.dof_pos - self.dof_pos_limits[:, 1]).clip(min=0.)
    return torch.sum(out_of_limits, dim=1)

def _reward_dof_vel_limits(self):
    # Penalize dof velocities too close to the limit
    # clip to max error = 1 rad/s per joint to avoid huge penalties
    return torch.sum(
        (torch.abs(self.dof_vel) - self.dof_vel_limits * self.cfg.rewards.soft_dof_vel_limit).clip(min=0., max=1.),
        dim=1)

def _reward_torque_limits(self):
    # penalize torques too close to the limit
    return torch.sum(
        (torch.abs(self.torques) - self.torque_limits * self.cfg.rewards.soft_torque_limit).clip(min=0.), dim=1)

def _reward_tracking_lin_vel(self):
    # Tracking of linear velocity commands (xy axes)
    if self.cfg.commands.global_reference:
        lin_vel_error = torch.sum(torch.square(self.commands[:, :2] - self.root_states[:, 7:9]), dim=1)
    else:
        lin_vel_error = torch.sum(torch.square(self.commands[:, :2] - self.base_lin_vel[:, :2]), dim=1)
    return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma)

# def _reward_tracking_lin_vel_long(self):
#     # Tracking of linear velocity commands (xy axes)
#     lin_vel_error = torch.sum(torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0]), dim=1)
#     return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma_long)
#
# def _reward_tracking_lin_vel_lat(self):
#     # Tracking of linear velocity commands (xy axes)
#     lin_vel_error = torch.sum(torch.square(self.commands[:, 1] - self.base_lin_vel[:, 1]), dim=1)
#     return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma_lat)

# def _reward_clipped_forward_progress(self):
#     # Tracking of linear velocity commands (xy axes)
#     forward_progress = self.base_lin_vel[:, 0] * self.dt
#     clipped_forward_progress = forward_progress.clip(max=self.cfg.rewards.max_velocity * self.dt)
#     return clipped_forward_progress
#
# def _reward_clipped_global_forward_progress(self):
#     # Tracking of linear velocity commands (xy axes)
#     forward_progress = self.root_states[:, 7] * self.dt
#     clipped_forward_progress = forward_progress.clip(max=self.cfg.rewards.max_velocity * self.dt)
#     return clipped_forward_progress

# def _reward_jump(self):
#     body_height = torch.mean(self.root_states[:, 2:3] - self.measured_heights, dim=-1)
#     jump_height_target = self.commands[:, 3] + self.cfg.rewards.base_height_target
#     reward = - torch.square(body_height - jump_height_target)
#     return reward

def _reward_tracking_ang_vel(self):
    # Tracking of angular velocity commands (yaw) 
    ang_vel_error = torch.square(self.commands[:, 2] - self.base_ang_vel[:, 2])
    return torch.exp(-ang_vel_error / self.cfg.rewards.tracking_sigma_yaw)

def _reward_feet_air_time(self):
    # Reward long steps
    # Need to filter the contacts because the contact reporting of PhysX is unreliable on meshes
    contact = self.contact_forces[:, self.feet_indices, 2] > 1.
    contact_filt = torch.logical_or(contact, self.last_contacts)
    self.last_contacts = contact
    first_contact = (self.feet_air_time > 0.) * contact_filt
    self.feet_air_time += self.dt
    rew_airTime = torch.sum((self.feet_air_time - 0.5) * first_contact,
                            dim=1)  # reward only on first contact with the ground
    rew_airTime *= torch.norm(self.commands[:, :2], dim=1) > 0.1  # no reward for zero command
    self.feet_air_time *= ~contact_filt
    return rew_airTime

def _reward_stumble(self):
    # Penalize feet hitting vertical surfaces
    return torch.any(torch.norm(self.contact_forces[:, self.feet_indices, :2], dim=2) > \
                        5 * torch.abs(self.contact_forces[:, self.feet_indices, 2]), dim=1)

def _reward_stand_still(self):
    # Penalize motion at zero commands
    return torch.sum(torch.abs(self.dof_pos - self.default_dof_pos), dim=1) * (
            torch.norm(self.commands[:, :2], dim=1) < 0.1)

def _reward_feet_contact_forces(self):
    # penalize high contact forces
    return torch.sum((torch.norm(self.contact_forces[:, self.feet_indices, :],
                                    dim=-1) - self.cfg.rewards.max_contact_force).clip(min=0.), dim=1)
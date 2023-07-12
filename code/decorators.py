from dataclass import PipelineStep


def step(name, description):
  # initialize step
  step = PipelineStep(name, description)

  # execute step
  def execute_step(func):
    def wrapper(**kwargs):
      # record inputs
      step.inputs = {'Source': kwargs['source_pointcloud'], 'Target': kwargs['target_pointcloud']}

      # execute function
      outputs, transforms = func(**kwargs)

      # record outputs
      step.output = outputs
      step.transform = transforms

      return step
    return wrapper
  return execute_step
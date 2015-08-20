#Contributing

##Coding Guidelines

Screenshooter follows the PEP8 standard where applicable. The following are additional rules to keep in mind:

1. All additions and deletions of methods / functions should have useful corresponding updates in tests that pass.
2. All additions and changes to the code should have a corresponding change to the documentation in the README.
  - If a function is referenced in the README it should contain an explanation of its arguments
    - If a Note is provided in that explanation it should be indented so that the Note refers to the parent indention i.e. **Note** here refers to the last bullet point, not the last number.
3. Any service added to the saves module requires the `save`, `collect_img` and `collect_images` methods.
4. Names should most closely resemble what they do i.e. the `Differ` class is in charge of diffing images or the `equals` method validates if two images are equal.

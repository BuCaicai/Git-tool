## git submodule
归档 commit 之间差异，包括 submodule
***
## Usage
```python archive.py [options | options[args]]```
```python archive.py --module demo --oldcom aaa*** --newcom bbb*** --output /data/demo/ ```

|     option     | args |         desc         |
|:--------------:|:----:|:--------------------:|
| ```--module``` |      |    submodule name    |
| ```--oldcom``` |      |   repo old commit    |
| ```--newcom``` |      |   repo new commit    |
| ```--output``` |      | tar file output path |
***
## Support
|            | old commmit | new commmit |
|:----------:|:-----------:|:-----------:|
| submodule  |      x      |      x      |
| submodule  |      x      |      v      |
| submodule  |      v      |      v      |
### 进行归档差分
1. 两个```commit```都有```submodule```
2. ```old commit```没有```submodule```，```new commit```有```submodule```
### 不进行归档差分
1. 两个```commit```都没有```submodule```
2. ```old commit```有```submodule```，```new commit```没有```submodule```
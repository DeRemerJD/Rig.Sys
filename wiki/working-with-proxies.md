# Working with proxies

Proxy transformations (world space translations and rotations) are saved in a user-specified json file.

To save proxy data to a file, build a character, transform proxies as desired, then call the character's `saveProxyTransformations()` method. This takes in a file path to save the data to.

To load proxy data from a file, use the `useSavedProxyData` and `proxyDataFile` arguments in the `build()` method. `useSavedProxyData` defaults to False and means that proxies will be built using their default transformation values.

The overall workflow might look like this:

Build the character

```python
character = ExampleCharacter()
character.build()
```

Then, manually transform the proxies as desired and save their positions.

```python
character = ExampleCharacter()
proxyDataFile = "C:/path/to/proxyData.json"

character.saveProxyTransformations(proxyDataFile)
```

Then, load the proxy data and build the character again.

```python
character = ExampleCharacter()
proxyDataFile = "C:/path/to/proxyData.json"

character.build(useSavedProxyData=True, proxyDataFile=proxyDataFile)
```

I usually like to have both the save and build commands in the same file, which I can toggle on and off by commenting/uncommenting the lines.

```python
character = ExampleCharacter()
proxyDataFile = "C:/path/to/proxyData.json"

character.build(usedSavedProxyData=True, proxyDataFile=proxyDataFile)
# character.saveProxyTransformations(proxyDataFile)
```

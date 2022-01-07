<p align="center">
<img src="https://github.com/jina-ai/docarray/blob/main/docs/_static/logo-light.svg?raw=true" alt="DocArray logo: The data structure for unstructured data" width="150px">
<br>
<b>The data structure for unstructured data</b>
</p>

<!-- start elevator-pitch -->

DocArray is a library for nested, unstructured data such as text, image, audio, video, 3D mesh. It allows deep learning engineers to easily preprocess, embed, search, recommend and transfer the data.

🌌 **All data types**: super-expressive data structure for representing complicated/mixed/nested text, image, video, audio, 3D mesh data.

🐍 **Pythonic API**: easy-to-use idioms and interfaces just as the native Python List. If you know how to Python, you know how to DocArray.

🧑‍🔬 **Data science powerhouse**: greatly facilitate data scientists work on embedding, matching, visualizing, evaluating via Torch/Tensorflow/ONNX/PaddlePaddle.

🚡 **Portable**: ready-to-wire at anytime with efficient and compact serialization from/to Protobuf, bytes, JSON, CSV, dataframe.

<!-- end elevator-pitch -->


## Install 

Requires Python 3.7+ and `numpy` only:
```
pip install docarray
```
[Additional features](https://docarray.jina.ai/#install) can be enabled by installing the full dependencies: `pip install "docarray[full]"`.

## [Documentation](https://docarray.jina.ai)

## Get Started

Let's use DocArray and [Totally Looks Like](https://sites.google.com/view/totally-looks-like-dataset) dataset to build simple meme image search. The dataset contains 6016 image-pairs stored in `/left` and `/right`. Images that shares the same filename are perceptually similar. For example, 

<table>
<thead>
  <tr>
    <th>left/00018.jpg</th>
    <th>right/00018.jpg</th>
    <th>left/00131.jpg</th>
    <th>right/00131.jpg</th>
  </tr>
</thead>
<tbody>
  <tr align="center">
    <td><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/left-00018.jpg?raw=true" alt="Visualizing top-9 matches using DocArray API" width="50%"></td>
    <td><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/right-00018.jpg?raw=true" alt="Visualizing top-9 matches using DocArray API" width="50%"></td>
    <td><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/left-00131.jpg?raw=true" alt="Visualizing top-9 matches using DocArray API" width="50%"></td>
    <td><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/right-00131.jpg?raw=true" alt="Visualizing top-9 matches using DocArray API" width="50%"></td>
  </tr>
</tbody>
</table>

Our problem is given an image from `/left` and find its most-similar image in `/right` (without looking at the filename of course).

### Load images

First load images and preprocess them with standard computer vision techniques:

```python
from docarray import DocumentArray, Document

left_da = DocumentArray.from_files('left/*.jpg')
```

To get a feeling of the data you will handle, plot them in one sprite image:

```python
left_da.plot_image_sprites()
```

<p align="center">
<a href="https://docarray.jina.ai"><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/sprite.png?raw=true" alt="Load totally looks like dataset with docarray API" width="60%"></a>
</p>

### Apply preprocessing

Let's do some standard computer vision preprocessing:

```python
def preproc(d: Document):
    return (d.load_uri_to_image_blob()  # load
             .set_image_blob_normalization()  # normalize color 
             .set_image_blob_channel_axis(-1, 0))  # switch color axis for the pytorch model later

left_da.apply(preproc)
```

Did I mention `apply` work in parallel?

### Embed images

Now convert images into embeddings using a pretrained ResNet50:

```python
import torchvision
model = torchvision.models.resnet50(pretrained=True)  # load ResNet50
left_da.embed(model, device='cuda')  # embed via GPU to speedup
```

This step takes ~30 seconds on GPU. Beside PyTorch, you can also use Tensorflow, PaddlePaddle, ONNX models in `.embed(...)`.

### Visualize embeddings

You can visualize the embeddings via tSNE in an interactive embedding projector:

```python
left_da.plot_embeddings()
```

<p align="center">
<a href="https://docarray.jina.ai"><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/tsne.gif?raw=true" alt="Visualizing embedding via tSNE and embedding projector" width="90%"></a>
</p>

Fun is fun, but recall our goal is to match left images against right images and so far we have only handled the left. Let's repeat the same procedure for the right:

```python
right_da = (DocumentArray.from_files('right/*.jpg')
                         .apply(preproc)
                         .embed(model, device='cuda'))
```

### Match nearest neighbours

We can now match the left to the right and take the top-9 results.

```python
left_da.match(right_da, limit=9)
```

Let's inspect what's inside `left_da` now:

```python
for d in left_da:
    for m in d.matches:
        print(d.uri, m.uri, m.scores['cosine'].value)
```

```text
left/02262.jpg right/03459.jpg 0.21102
left/02262.jpg right/02964.jpg 0.13871843
left/02262.jpg right/02103.jpg 0.18265384
left/02262.jpg right/04520.jpg 0.16477376
...
```

Better see it.

```python
(DocumentArray(left_da[8].matches, copy=True)
    .apply(lambda d: d.set_image_blob_channel_axis(0, -1)
                      .set_image_blob_inv_normalization())
    .plot_image_sprites('result.png'))
```

<p align="center">
<a href="https://docarray.jina.ai"><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/9nn-left.jpeg?raw=true" alt="Visualizing top-9 matches using DocArray API" height="250px"></a>
<a href="https://docarray.jina.ai"><img src="https://github.com/jina-ai/docarray/blob/main/.github/README-img/9nn.png?raw=true" alt="Visualizing top-9 matches using DocArray API" height="250px"></a>
</p>

What we did here is reverting the preprocessing steps (i.e. switching axis and normalizing) on the copied matches, so that one can visualize them using image sprites.  

### Quantitative evaluation

Serious as you are, visual inspection is surely not enough. Let's calculate the recall@K. First we construct the groundtruth matches:

```python
groundtruth = DocumentArray(
    Document(uri=d.uri, matches=[Document(uri=d.uri.replace('left', 'right'))]) for d in left_da)
```

Here we create a new DocumentArray with real matches by simply replacing the filename, e.g. `left/00001.jpg` to `right/00001.jpg`. That's all we need: if the predicted match has the identical `uri` as the groundtruth match, then it is correct.

Now let's check recall rate from 1 to 5 over the full dataset:

```python
for k in range(1, 6):
    print(f'recall@{k}',
          left_da.evaluate(
            groundtruth,
            hash_fn=lambda d: d.uri,
            metric='recall_at_k',
            k=k,
            max_rel=1))
```

```text
recall@1 0.02726063829787234
recall@2 0.03873005319148936
recall@3 0.04670877659574468
recall@4 0.052194148936170214
recall@5 0.0573470744680851
```

More metrics can be used such as `precision_at_k`, `ndcg_at_k`, `hit_at_k`. 



### Save results

You can save a DocumentArray to binary, JSON, dict, dataframe, CSV or Protobuf message with/without compression. In its simplest form,

```python
left_da.save('left_da.bin')
```

To reuse it, do `left_da = DocumentArray.load('left_da.bin')`.

If you want to transfer a DoucmentArray from one machine to another or share it with your colleagues, you can do:

```python
left_da.push(token='my_shared_da')
```

Now anyone who knows the token `my_shared_da` can pull and work on it.

```python
left_da = DocumentArray.pull(token='my_shared_da')
```



Intrigued? That's only scratching the surface of what DocArray is capable of. [Read our docs to learn more](https://docarray.jina.ai).

<!-- start support-pitch -->
## Support

- Use [Discussions](https://github.com/jina-ai/docarray/discussions) to talk about your use cases, questions, and
  support queries.
- Join our [Slack community](https://slack.jina.ai) and chat with other community members about ideas.
- Join our [Engineering All Hands](https://youtube.com/playlist?list=PL3UBBWOUVhFYRUa_gpYYKBqEAkO4sxmne) meet-up to discuss your use case and learn Jina's new features.
    - **When?** The second Tuesday of every month
    - **Where?**
      Zoom ([see our public events calendar](https://calendar.google.com/calendar/embed?src=c_1t5ogfp2d45v8fit981j08mcm4%40group.calendar.google.com&ctz=Europe%2FBerlin)/[.ical](https://calendar.google.com/calendar/ical/c_1t5ogfp2d45v8fit981j08mcm4%40group.calendar.google.com/public/basic.ics))
      and [live stream on YouTube](https://youtube.com/c/jina-ai)
- Subscribe to the latest video tutorials on our [YouTube channel](https://youtube.com/c/jina-ai)

## Join Us

DocArray is backed by [Jina AI](https://jina.ai) and licensed under [Apache-2.0](./LICENSE). [We are actively hiring](https://jobs.jina.ai) AI engineers, solution engineers to build the next neural search ecosystem in opensource.

<!-- end support-pitch -->

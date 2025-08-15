# Binary Structure
**Terjemahan dalam progress**

Bagian ini akan menjelaskan struktur binary dari beberapa file. Semua file di kompress menggunakan C data type dengan little endian dan menggunakan 32-bit size.

Angka double/triple float biasanya didefinisikan menggunakan variabel `D3DXVECTOR3`, yang mengandung [x, y, z].

Quaternion selalu didefinisikan menggunakan variabel `D3DXQUATERNION`, yang mengandung [x, y, z, w], urutan mungkin harus diubah tergantung program yang dipakai.

Dikarenakan format 3d bersumber dari DirectX, [sistem koordinat harus disesuaikan](https://x.com/FreyaHolmer/status/644881436982575104) tergantung program yang dipakai. Intinya, (x, y, z) akan terbentuk menjadi (x, z, -y) di Blender. Tentu saja, solusi paling mudah yaitu cukup dengan meng-import file tersebut sebagai adanya, lalu putar model setelahnya.

![Here, have a coordinate system chart!](https://pbs.twimg.com/media/CPMUP9bUwAAcDr8?format=jpg&name=orig)

## Token Definition
Token ini biasanya digunakan untuk headers

| Definition                 | Value |
| -------------------------- | ----- |
| SKELETON_TOKEN             | SKL\0 |
| MATERIAL_TOKEN             | MTL\0 |
| ANIMATION_TOKEN            | ANI\0 |
| MESH_TOKEN                 | MSH\0 |
| FONT_TOKEN                 | FNT\0 |
| COL_MESH_TOKEN             | CMS\0 |
| PGF_TOKEN                  | PGF\0 |
| ANIMATE_EFFECT_TOKEN       | AFX\0 |
| OUTLINE_EDGE_TOKEN         | EDG\0 |
| SKELETON_VERSION           | 1000  |
| MESH_VERSION               | 2000  |
| VERTEX_COLOR_MESH_VERSION  | 2001  |
| MESH_CONTROL_POINT_VERSION | 2002  |
| MATERIAL_VERSION           | 3000  |
| ANIMATION_VER_DEFAULT      | 4000  |
| ANIMATION_VER_COMP4        | 4001  |
| ANIMATION_VER_COMP8        | 4002  |
| FONT_VERSION               | 5000  |
| COL_MESH_VERSION           | 5000  |
| ANIMATE_EFFECT_VERSION     | 6000  |
| OUTLINE_EDGE_VERSION       | 7000  |

## 3D Types

### Vertex Component
Digunakan untuk vertex mask, untuk mengindikasikan bahwa komponen tersebut ada atau tidak.

Untuk menggunakan ini, gunakan operasi bitwise AND operator dengan komponen, contoh: `vertex_mask & IOFVF_UV0`, akan menghasilkan `1` jikalau mengandung UV map, atau `0` jikalau tidak.

| Vertex Component  | Value | Actual Value          |
| ----------------- | ----- | --------------------- |
| IOFVF_POSITION    | 1<<0  | 1                     |
| IOFVF_POSITION2   | 1<<1  | 2                     |
| IOFVF_POSITIONW   | 1<<2  | 4                     |
| IOFVF_WEIGHTS     | 1<<3  | 8                     |
| IOFVF_INDICES     | 1<<4  | 16                    |
| IOFVF_NORMAL      | 1<<5  | 32                    |
| IOFVF_COLOR0      | 1<<6  | 64                    |
| IOFVF_COLOR1      | 1<<7  | 128                   |
| IOFVF_UV0         | 1<<8  | 256                   |
| IOFVF_UV1         | 1<<9  | 512                   |
| IOFVF_UV2         | 1<<10 | 1024                  |
| IOFVF_UV3         | 1<<11 | 2048                  |
| IOFVF_TANGENT     | 1<<12 | 4096                  |
| IOFVF_BINORMAL    | 1<<13 | 8192                  |
| IOFVF_END         |       | (tidak didefinisikan) |

### Mesh Type
Kamu tidak perlu menggunakan tipe mesh lain selain dari static, animation, dan lightmap, karena hanya ketiga tipe tersebut yang umum digunakan dalam game.

| Index | Type                      |
| ----- | ------------------------- |
| 0     | MT_STATIC                 |
| 1     | MT_ANIMATION              |
| 2     | MT_LIGHTMAP               |
| 3     | MT_BILLBOARD              |
| 4     | MT_NORMAL_BILLBOARD       |
| 5     | MT_ANIMATE_EFFECT         |
| 6     | MT_STATIC_VERTEX_COLOR    |

## SKL

### Header
Selalu tersedia

| Type  | Size (in bytes)   | Description                                   |
| ----- | ----------------- | --------------------------------------------- |
| int   | 4                 | Signature, selalu sama dengan skeleton token     |
| int   | 4                 | Version, selalu sama dengan skeleton version     |

### Biped

| Type  | Size (in bytes)   | Description                                   |
| ----- | ----------------- | --------------------------------------------- |
| int   | 4                 | Biped Count. Number of bones                  |

___

Struktur ini hanya tersedia jika jumlah biped ada diatas 0, berulang tergantung jumlah biped yang dimiliki

| Type  | Size (in bytes)       | Description                                                                                                                           |
| ----- | -----------------     | ------------------------------------------------------------------------------------------------------------------------------------- |
| int | 4 | Panjang nama tulang biped |
| char | variabel | Nama tulang biped, ukuran tergantung panjang nama tulang biped |
| float | 12 (masing-masing berisi 4) | LocalTM Position. Mungkin berisi lokasi tulang relatik terhadap tulang induk |
| float | 16 (masing-masing berisi 4) | LocalTM Quaternion. Mungkin berisi rotasi tulang relatif terhadap tulang induk |
| float | 12 (masing-masing berisi 4) | ObjectTM Inverse Position. Kemungkinan menunjukkan posisi tulang relatif terhadap asal dunia. Tidak digunakan dalam skrip karena matriks disediakan |
| float | 16 (masing-masing berisi 4) | ObjectTM Inverse Quaternion. Kemungkinan menunjukkan rotasi tulang relatif terhadap asal dunia. Tidak digunakan dalam skrip karena matriks disediakan |
| float | 64 (masing-masing berisi 4) | Matriks Tulang. Perlu ditransposisikan terlebih dahulu |
| int | 4 | Panjang nama tulang induk |
| char | variabel | Nama tulang induk, ukurannya bergantung pada panjang nama tulang induk, defaultnya adalah `NoParent` jika tidak ada tulang induk |
| int | 4 | Jumlah anak |

___

Struktur ini hanya tersedia jika jumlah child ada diatas 0, berulang tergantung jumlah child yang dimiliki
This structure only available if child count is more than 0, it loops for each child it has

| Type  | Size (in bytes)       | Description                                                                                                                   |
| ----- | -----------------     | ----------------------------------------------------------------------------------------------------------------------------- |
| int   | 4                     | Child bone name length                                                                                                        |
| char  | variable              | The child bone name, size is depending on the child bone name length|

### Linked Skeleton
Always available

| Type  | Size (in bytes)       | Description                                                                                                                               |
| ----- | -----------------     | ----------------------------------------------------------------------------------------------------------------------------------------- |
| int   | 4                     | Linked skeleton name length                                                                                                               |
| char  | variable              | The linked skeleton name, size is depending on the linked skeleton name length. Likely used for animation that uses multiple skeleton?    |

## ANI
Unless specified otherwise, all time mentioned in this content is always in miliseconds

### Header
Always available

| Type  | Size (in bytes)   | Description                                       |
| ----- | ----------------- | ---------------------------------------------     |
| int   | 4                 | Signature, always equal to animation token        |
| int   | 4                 | Version, can be either default, comp4, or comp8   |

### Events
Always available

| Type  | Size (in bytes)   | Description                                   |
| ----- | ----------------- | --------------------------------------------- |
| int   | 4                 | Event Count. Number of events                 |

___

This structure only available if event count is more than 0, loops for each event it has

| Type  | Size (in bytes)   | Description                                                   |
| ----- | ----------------- | ---------------------------------------------                 |
| int   | 4                 | Event type length                                             |
| char  | variable          | The event type, size is depending on the event type length    |
| int   | 4                 | Event name length                                             |
| char  | variable          | The event name, size is depending on the event name length    |
| float | 4                 | Event time                                                    |

### Tracks
Always available

| Type  | Size (in bytes)   | Description                                   |
| ----- | ----------------- | --------------------------------------------- |
| int   | 4                 | Total time. The total duration of animation   |
| int   | 4                 | Total track count                             |

___

This structure only available if total track count is more than 0, loops for each track it has

| Type  | Size (in bytes)   | Description                                                               |
| ----- | ----------------- | ------------------------------------------------------------------------- |
| int   | 4                 | Biped bone name length                                                    |
| char  | variable          | The biped bone name, size is depending on the biped bone name length      |
| float | 4                 | Weight influence                                                          |
| int   | 4                 | Keyframe count                                                            |

#### DEFAULT
If version is equal to `ANIMATION_VER_DEFAULT`, then this structure will be used. Loops for each keyframe it has

| Type  | Size (in bytes)       | Description               |
| ----- | -----------------     | ------------------------- |
| float | 16 (contains 4 each)  | Quaternion rotation       |
| float | 12 (contains 4 each)  | Vector Transformation     |
| int   | 4                     | Time                      |


#### COMP 4
If version is equal to `ANIMATION_VER_COMP4`, then this structure will be used. Loops for each keyframe it has

| Type  | Size (in bytes)       | Description           |
| ----- | -----------------     | --------------------- |
| long  | 4                     | Packed rotation       |
| float | 12 (contains 4 each)  | Vector Transformation |
| int   | 4                     | Time                  |

#### COMP 8
If version is equal to `ANIMATION_VER_COMP8`, then this structure will be used. Loops for each keyframe it has

| Type  | Size (in bytes)       | Description               |
| ----- | -----------------     | ------------------------- |
| long  | 4                     | Packed rotation, dwHigh   |
| long  | 4                     | Packed rotation, dwLow    |
| float | 12 (contains 4 each)  | Vector Transformation     |
| int   | 4                     | Time                      |

## MSH

### Header
Always available

| Type  | Size (in bytes)       | Description                                       |
| ----- | --------------------- | ------------------------------------------------- |
| int   | 4                     | Signature, always equal to mesh token             |
| int   | 4                     | Version, usually equal to mesh version            |
| int   | 4                     | Mesh Type. Correspond to mesh type index          |
| long  | 4                     | Vertex mask.                                      |
| long  | 4                     | Vertex mask.                                      |
| float | 12 (contains 4 each)  | Bounding box minimum                              |
| float | 12 (contains 4 each)  | Bounding box maximum                              |
| float | 4                     | Bounding radius                                   |

### Submesh
Always available

| Type  | Size (in bytes)   | Description       |
| ----- | ----------------- | ----------------- |
| int   | 4                 | Submesh count     |

___

This structure only available if submesh count is more than 0, loops for each submesh it has

The main mesh is counted towards the submesh, so basically submesh is just the total amount of mesh it has. Separating mesh is useful if you want to have different material/animation for each mesh.
The submesh doesn't contain the actual submesh, but rather an index on where to split the mesh.

| Type  | Size (in bytes)   | Description                               |
| ----- | ----------------- | ----------------------------------------- |
| int   | 4                 | Min index. Starting index for vertices    |
| int   | 4                 | Vertex count                              |
| int   | 4                 | Index Start. Starting index for faces     |
| int   | 4                 | Face count                                |

### Vertices Count
Always available

| Type  | Size (in bytes)   | Description                               |
| ----- | ----------------- | ----------------------------------------- |
| int   | 4                 | Vertex count. Total amount of vertices    |

### Components
Any structure listed on this section only available if vertex mask return corresponding value.

Also, all **structure listed in this section loops for each vertex count, unless specified otherwise**

#### Vertices/Position
Component: `IOFVF_POSITION`

| Type  | Size (in bytes)       | Description                                |
| ----- | -----------------     | ------------------------------------------ |
| float | 12 (contains 4 each)  | Position. Vector position of each vertices |

#### Normals
Component: `IOFVF_NORMAL`

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| float | 12 (contains 4 each)  | Normals. Normals of each vertices         |

#### Tangent
Component: `IOFVF_TANGENT`

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| float | 12 (contains 4 each)  | Tangent. Tangent of each vertices         |

#### Binormal
Component: `IOFVF_BINORMAL`

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| float | 12 (contains 4 each)  | Binormal. Binormal of each vertices       |

#### Vertex Color
Component: `IOFVF_COLOR0`

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| long  | 4                     | Vertex color. The color of each vertices  |

#### UV map/Lightmap UV
Component: `IOFVF_UV0`

If this mesh type if a lightmap, then this UV is a lightmap UV, otherwise it's the main UV map.

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| float | 8 (contains 4 each)   | UV map. 2D vector of the UV map           |

#### Secondary UV map
Component: `IOFVF_UV1`

Only for lightmap. This contains the main UV map for the main texture

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| float | 8 (contains 4 each)   | UV map. 2D vector of the UV map           |

#### Weights
Component: `IOFVF_WEIGHTS`\* and `IOFVF_INDICES`\*

\* The source code does not check if both flags are true, and instead it is processed individually. But you still need both component if you want to include weights

**This structure does not loop for each vertex count**

| Type  | Size (in bytes)   | Description                                               |
| ----- | ----------------- | --------------------------------------------------------- |
| int   | 4                 | Biped index count. Total amount of vertex group it has    |

___

This structure only available if biped index count is more than 0, it loops for each biped index it has

| Type  | Size (in bytes)   | Description                                                   |
| ----- | ----------------- | ------------------------------------------------------------- |
| int   | 4                 | Biped name length                                             |
| char  | variable          | The biped name, size is depending on the biped name length    |

___

Always available

Since direct-x only support maximum of 4 bone influence per vertex, each array contains 4 float of weight. However, Lost Saga have slightly different operations, as soon it hit zero weights, it will break the loop and continue to the next indices. So it is recommended to sort the weights first.

| Type  | Size (in bytes)       | Description                               |
| ----- | --------------------- | ----------------------------------------- |
| float | 16 (contains 4 each)  | Weight. Array of weights                  |
| float | 16 (contains 4 each)  | Biped ID. Order always paired with weight |

#### Billboard Center
Component: `IOFVF_POSITION2`

Unused. None of the mesh file has this flag

| Type  | Size (in bytes)       | Description                                |
| ----- | -----------------     | ------------------------------------------ |
| float | 12 (contains 4 each)  | Position. Vector position of each vertices |

### Faces
Always available

| Type  | Size (in bytes)       | Description                                |
| ----- | --------------------- | ------------------------------------------ |
| int   | 4                     | Face count                                 |

___

This structure only available if face count is more than 0, it loops for each face it has. **Face count must be multiplied by 3**

| Type  | Size (in bytes)       | Description                                |
| ----- | -----------------     | ------------------------------------------ |
| float | 12 (contains 4 each)  | Faces. Correspond to vertices index        |

### Mesh Control Point
This structure only available if mesh version is equal to `MESH_CONTROL_POINT_VERSION` (2002)

This mesh type is only used for older mesh, especially weapons, it is no longer used again ever since

| Type  | Size (in bytes)       | Description   |
| ----- | --------------------- | ------------- |
| int   | 4                     | Point Count   |

___

This structure only available if point count is more than 0, it loops for each point it has

| Type  | Size (in bytes)       | Description                                                               |
| ----- | --------------------- | ------------------------------------------------------------------------- |
| int   | 4                     | Type index length                                                         |
| char  | variable              | The type index, size is depending on the type index length                |
| int   | 4                     | Linked biped name length                                                  |
| char  | variable              | The linked biped name, size is depending on the linked biped name length  |
| int   | 4                     | Extra info length                                                         |
| char  | variable              | The extra info, size is depending on the extra info length                |
| float | 12 (contains 4 each)  | Vector point                                                              |

## CMS

### Header
Always available

| Type  | Size (in bytes)               | Description                                                               |
| ----- | ----------------------------- | ------------------------------------------------------------------------- |
| int   | 4                             | Signature, always equal to col mesh token                                 |
| int   | 4                             | Version, always equal to col mesh version                                 |

### Mesh

| Type  | Size (in bytes)               | Description                                                               |
| ----- | ----------------------------- | ------------------------------------------------------------------------- |
| int   | 4                             | Vertex count                                                              |
| float | variable (contains 4 each)    | Position. Vector position of each vertices. Loops for each vertex it has  |
| int   | 4                             | Face count                                                                |
| float | variable (contains 4 each)    | Faces. Correspond to vertices index. Loops for each face it has           |
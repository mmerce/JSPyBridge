import { python, PyClass } from '../Bridge.js'

const f = await python('./pyImp.py')
const demo = await python('./demo.py')

async function it (what, fn) {
  console.log('it', what)
  await fn()
}

await it('does function calls', async function () {
  console.log('add inverse', await f.add_inverse(3, 2))
  const complex = await f.complex_num()
  console.log('complex', complex)
  console.log('real & complex', await complex.real, await complex.imag)
  console.log('FABC - this will fail', f.a.b.c)
})

await it('declares classes', async function () {
  class MyClas extends PyClass {
    someMethod() {
      return 3
    }
  }
  
  await f.some_event(async (message, method) => {
    // Call a Python function passed as a paramater
    console.log('Message', message, await method())
  }, new MyClas())
})

await it('consumes classes', async function () {
  const { DemoClass, add } = demo
  const demoInst = await DemoClass(3)
  console.log(demoInst)
})

// process.exit(0)

python.exit()